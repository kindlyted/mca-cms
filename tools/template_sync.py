#!/usr/bin/env python3
"""
template_sync.py — Bidirectional template <-> derived-site code sync.

Motivation
----------
The template is copied out wholesale to create a new site (Copy-Item the whole
repo).  That mixes *template code* (pages/components/server/tools/...) with
*site content* (data/, input/, generated utils/config.ts, brand-injected i18n).
When a fix is made in a derived site, it can't simply be copied back file-for-file,
because the site's copy of some files is polluted with site-specific data.

This script syncs ONLY the files listed in TEMPLATE_CODE (relative to repo root),
in either direction, using content hashes to show diffs before applying.

Usage
-----
  # Preview what changed in the derived site vs the template (no writes):
  python tools/template_sync.py --to-template SITE_DIR

  # Actually copy the changed template-code files from the derived site back:
  python tools/template_sync.py --to-template SITE_DIR --apply

  # Push template code updates INTO a derived site (template -> site):
  python tools/template_sync.py --to-site SITE_DIR [--apply]

  # Also include "half-generated" files (utils/config.ts, i18n/locales, nuxt.config.ts)
  python tools/template_sync.py --to-template SITE_DIR --include-generated --apply

Conventions
-----------
- Relative paths are relative to the template repo root.
- "*" anywhere in a path segment matches any text (glob).
- Directories in TEMPLATE_CODE are included recursively.
- Files in GENERATED are NEVER synced unless --include-generated, and even then
  only under --apply (they are brand/site-injected, usually need manual review).
"""

import argparse
import hashlib
import re
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Template code inventory — the ONLY files that are considered "template".
# Add anything here that should flow between template and derived sites.
# ---------------------------------------------------------------------------

TEMPLATE_CODE = [
    # Source code (auto-synced)
    "pages/",
    "components/",
    "composables/",
    "layouts/",
    "plugins/",
    "server/",
    "types/",
    "config/",
    "tools/sitegen/",
    "cms/",
    "app.vue",
    "error.vue",
    "i18n.config.ts",
    "tsconfig.json",
    "ecosystem.config.cjs",
    "package.json",
    "package-lock.json",
    ".env.example",
]

# Half-generated files: template structure + site-injected brand/localized data.
# Only touched with --include-generated --apply.
GENERATED = [
    "utils/config.ts",          # sitegen writes this from company.json
    "nuxt.config.ts",           # sitegen rewrites the i18n.locales array
    "site.config.json",         # sitegen writes nav/footer from company.json
    "i18n/locales/*.json",      # sitegen injects brand copy per language
]

# Never synced, ever (site content / build artifacts / env).
ALWAYS_IGNORE = [
    "data/",
    "input/",
    "cms/.env",
    "cms/.env.*",
    ".output/",
    ".nuxt/",
    ".nitro/",
    ".data/",
    "dist/",
    "node_modules/",
    ".git/",
    ".env",
    ".env.*",
    "!.env.example",
    "prisma/*.db",
    "prisma/*.db-journal",
    "logs/",
    "**/__pycache__/",
    "**/*.pyc",
    "venv/",
    ".venv/",
]


def _compile(patterns):
    out = []
    for p in patterns:
        negate = p.startswith("!")
        pat = p[1:] if negate else p
        regex = fnmatch_to_regex(pat)
        out.append((regex, negate))
    return out


def fnmatch_to_regex(pattern):
    """Translate a path pattern with '*' into an anchored regex.

    Supported syntax:
      - "*" matches any chars within a path segment (no "/")
      - "**" matches zero or more directory levels
      - trailing "/" means "this directory and everything under it"
    """
    # Normalise to forward slashes
    p = pattern.replace("\\", "/").lstrip("/")
    trailing_slash = p.endswith("/")
    parts = [x for x in p.split("/") if x not in ("", ".")]

    regex = "^"
    if "**" in parts:
        # Handle leading "**/" as zero-or-more directory levels
        while "**" in parts:
            idx = parts.index("**")
            # everything before ** as literal segments joined by /
            if idx > 0:
                regex += "/".join(re.escape(x) for x in parts[:idx]) + "/"
            parts = parts[idx + 1:]
            # if ** is followed by more segments
            if parts:
                regex += r"(?:[^/]+/)*"
            else:
                regex += r".*"
        if parts:
            regex += "/".join(re.escape(x) for x in parts)
    else:
        segs = []
        for part in parts:
            if "*" in part:
                segs.append(re.escape(part).replace(r"\*", r"[^/]*"))
            else:
                segs.append(re.escape(part))
        regex += "/".join(segs)

    if trailing_slash:
        regex += "(?:/.*)?"
    else:
        regex += "$"
    return re.compile(regex)


def match(compiled, rel):
    rel = rel.replace("\\", "/")
    include = None
    for regex, negate in compiled:
        if regex.match(rel):
            include = not negate
    return include


def is_template_code(rel):
    return match(_compile(TEMPLATE_CODE), rel) is True


def is_generated(rel):
    return match(_compile(GENERATED), rel) is True


def is_ignored(rel):
    return match(_compile(ALWAYS_IGNORE), rel) is True


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def walk_code(base: Path):
    """Yield (rel_path, abs_path) for every template-code file under base."""
    results = {}
    for root, dirs, files in os_walk(base):
        root_rel = Path(root).relative_to(base)
        # prune ignored directories
        keep = []
        for d in dirs:
            rel = (root_rel / d).as_posix()
            if not is_ignored(rel + "/"):
                keep.append(d)
        dirs[:] = keep
        for f in files:
            rel = (root_rel / f).as_posix()
            if rel.startswith("./"):
                rel = rel[2:]
            if is_ignored(rel):
                continue
            if not is_template_code(rel):
                continue
            results[rel] = root / f
    return results


def os_walk(base: Path):
    import os
    for root, dirs, files in os.walk(str(base)):
        yield Path(root), dirs, files


def collect_files(repo: Path, include_generated: bool):
    files = walk_code(repo)
    if include_generated:
        for root, dirs, files in os_walk(repo):
            root_rel = Path(root).relative_to(repo)
            for f in files:
                rel = (root_rel / f).as_posix()
                if is_generated(rel) and not is_ignored(rel):
                    files[rel] = root / f
    return files


def build_report(template: Path, other: Path, include_generated: bool):
    """Return (modified_in_other, only_in_template, only_in_other) list of rels."""
    tpl_files = collect_files(template, include_generated)
    oth_files = collect_files(other, include_generated)

    modified, only_tpl, only_oth = [], [], []
    for rel, tpl_abs in tpl_files.items():
        oth_abs = oth_files.get(rel)
        if oth_abs is None:
            only_tpl.append(rel)
        elif oth_abs.exists() and tpl_abs.exists():
            if sha1(tpl_abs) != sha1(oth_abs):
                modified.append(rel)
    for rel in oth_files:
        if rel not in tpl_files:
            only_oth.append(rel)
    return sorted(modified), sorted(only_tpl), sorted(only_oth)


def copy_one(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main():
    parser = argparse.ArgumentParser(description="Bidirectional template/site code sync")
    parser.add_argument("site", help="Path to the derived site directory")
    parser.add_argument("--to-template", dest="to_template", action="store_true",
                        help="Sync site -> template (copy fixes back into the template)")
    parser.add_argument("--to-site", dest="to_site", action="store_true",
                        help="Sync template -> site (push template updates into the site)")
    parser.add_argument("--apply", action="store_true",
                        help="Actually copy files (default is dry-run preview)")
    parser.add_argument("--include-generated", action="store_true",
                        help="Also include half-generated files (config.ts, i18n, nuxt.config)")
    parser.add_argument("--template", default=None,
                        help="Template repo root (default: repo containing this script)")
    args = parser.parse_args()

    if args.to_template == args.to_site:
        parser.error("specify exactly one of --to-template or --to-site")
    to_template = args.to_template

    template = Path(args.template).resolve() if args.template else Path(__file__).resolve().parent.parent
    site = Path(args.site).resolve()

    if not template.is_dir():
        print(f"ERROR: template dir not found: {template}")
        return 1
    if not site.is_dir():
        print(f"ERROR: site dir not found: {site}")
        return 1
    if template == site:
        print("ERROR: template and site must be different directories")
        return 1

    modified, only_tpl, only_oth = build_report(template, site, args.include_generated)

    print(f"Template : {template}")
    print(f"Site     : {site}")
    print(f"Mode     : {'TO TEMPLATE (site -> template)' if to_template else 'TO SITE (template -> site)'}")
    print(f"Apply    : {'YES (writing files)' if args.apply else 'DRY-RUN (preview only)'}")
    print()

    # Direction: what is the "source" set of files we'd copy?
    if to_template:
        # Copy site's modified files + site-only files back to template
        to_copy = modified + only_oth
        from_dir, to_dir = site, template
        label = "Changed in site"
    else:
        # Copy template's modified files + template-only files down to site
        to_copy = modified + only_tpl
        from_dir, to_dir = template, site
        label = "Changed in template"

    if not to_copy:
        print("No differences found. Nothing to sync.")
        return 0

    print(f"Files to sync ({len(to_copy)}):")
    for rel in to_copy:
        print(f"  {rel}")

    if only_tpl and to_template:
        print(f"\nNote: {len(only_tpl)} file(s) exist in template but not site (not synced in this direction).")
    if only_oth and not to_template:
        print(f"\nNote: {len(only_oth)} file(s) exist in site but not template (not synced in this direction).")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to copy.")
        return 0

    n = 0
    for rel in to_copy:
        src = from_dir / rel
        if not src.exists():
            continue
        dst = to_dir / rel
        if not src.is_file():
            continue
        copy_one(src, dst)
        n += 1
        print(f"  copied: {rel}")
    print(f"\nDone. Copied {n} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
