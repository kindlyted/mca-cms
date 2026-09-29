#!/usr/bin/env python3
"""
MCA-CMS Site Generator — "WordPress-style" quick start.

Standard input directory:
    input/
      company.json          # REQUIRED site manifest (company info + nav/footer + copy overrides)
      tags.json             # OPTIONAL tags dictionary override (config/tags.json)
      content/
        products/{lang}/*.json     # per-language product content (商品站)
        services/{lang}/*.json     # per-language service content (服务站)
        partners/{lang}/*.json     # per-language partner content (中介/合作)
        blogs/{lang}/*.json        # per-language blog articles (所有站点)
      assets/
        logo/logo.png              # brand logo  -> public/images/logo/logo.png
        hero/hero-bg.webp          # homepage hero -> public/images/ (copy as-is)
        products/{category}/{id}/* # product images -> data/assets/products/{category}/{id}/
        services/{id}/*            # service images -> data/assets/services/{id}/
        partners/{id}/*            # partner images  -> data/assets/partners/{id}/
        blogs/{id}/*               # blog images     -> data/assets/blogs/{id}/

What the script does:
  1. Validate company.json and every content JSON (required fields).
  2. Generate utils/config.ts from the manifest.
  2b. Generate site.config.json (nav + footer) from the manifest's nav/footer fields.
  3. Inject brand/copy overrides into i18n/locales/{lang}.json (template injection,
     no LLM). "YourBrand"/"Your Company" placeholders are replaced automatically.
  4. Copy validated content into data/ (gitignored, per-deployment).
  5. Copy images into data/assets/ + public/images/logo/ + public/images/hero/
     and rewrite cover URLs to /api/assets/{type}/{id}/{filename}.
  6. Sync nuxt.config.ts i18n.locales with manifest["languages"].
  7. Run npm install (if needed) -> npx prisma generate -> npm run build
     -> .output/ ready to deploy.

Usage:
    # Generate in place into the current template repo (default):
    python tools/sitegen/generate.py [--input DIR] [--no-build]
    # Scaffold a fresh, complete site at a NEW directory and generate into it:
    python tools/sitegen/generate.py --input DIR --out ./my-site [--no-build]
    # Generate into an existing repo directory:
    python tools/sitegen/generate.py [--repo DIR] [--no-build]
    npm run sitegen            # alias for the same command

Exit codes: 0 ok, 1 validation/generation error, 2 build error.
"""

import argparse
import copy
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_REPO = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = "input"

# ---------------------------------------------------------------------------
# Static templates
# ---------------------------------------------------------------------------

# i18n placeholders that are replaced everywhere in all locale files
PLACEHOLDER_REPLACEMENTS = (
    ("YourBrand", "shortName"),
    ("Your Company", "name"),
    ("yourdomain.com", "host"),
)

LOCALE_META = {
    "en": {"iso": "en-US", "name": "English"},
    "fr": {"iso": "fr-FR", "name": "Français"},
    "de": {"iso": "de-DE", "name": "Deutsch"},
    "es": {"iso": "es-ES", "name": "Español"},
}

DEFAULT_LANGUAGES = ["en", "fr", "de"]

CONTENT_DIRS = {
    "service": "services",
    "partner": "partners",
    "blog": "blogs",
    "product": "products",
}

# input/content/ folder name per entity type (plural, matches the pages)
INPUT_FOLDER = {
    "service": "services",
    "partner": "partners",
    "blog": "blogs",
    "product": "products",
}

ASSET_TYPES = ("services", "partners", "blogs", "products")

# YAML template for the generated GitHub Actions deploy workflow.
# __UPPER_SNAKE__ placeholders are replaced from company["deploy"] (see
# build_deploy_config). Kept as a plain string so ${{ secrets.* }} braces are safe.
DEPLOY_YAML_TEMPLATE = """\
name: Build & Deploy

on:
  push:
    branches: [__BRANCH__]
  workflow_dispatch: # 支持手动触发

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: __NODE_VERSION__
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Generate Prisma Client
        run: npx prisma generate

      - name: Build Nuxt
        run: npm run build

      - name: Deploy to server
        uses: appleboy/scp-action@v1
        with:
          host: ${{ secrets.__SECRETS_HOST__ }}
          username: __SSH_USER__
          key: ${{ secrets.__SECRETS_KEY__ }}
          source: "__SCP_SOURCE__"
          target: "__STAGING_PATH__"

      - name: Deploy & Restart service
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.__SECRETS_HOST__ }}
          username: __SSH_USER__
          key: ${{ secrets.__SECRETS_KEY__ }}
          script: |
            # 1. 先停掉 PM2 进程（防止替换代码期间有请求进来）
            sudo -u __RUN_USER__ bash -c 'cd __SERVER_PATH__ && pm2 stop __PM2_NAME__ || true'

            # 2. 删除旧产物（用 root 确保能删掉所有文件）
            sudo rm -rf __SERVER_PATH__/.output || true

            # 3. 复制新产物并修正权限
            sudo cp -r __STAGING_PATH__/.output __SERVER_PATH__/
            sudo cp __STAGING_PATH__/ecosystem.config.cjs __SERVER_PATH__/
            sudo chown -R __RUN_USER__:__RUN_USER__ __SERVER_PATH__/.output || true
            sudo chown __RUN_USER__:__RUN_USER__ __SERVER_PATH__/ecosystem.config.cjs || true

            # 4. 清理临时文件
            sudo rm -rf __STAGING_PATH__ || true

            # 5. 启动 PM2
            sudo -u __RUN_USER__ bash -c 'cd __SERVER_PATH__ && pm2 start __PM2_NAME__ || pm2 start ecosystem.config.cjs'
"""

# One-time environment setup script written into every generated site.
# Installs CMS Python deps, runs npm install, and creates the SQLite DB.
# (.env is created separately by ensure_env() before the build step.)
SETUP_PS1_TEMPLATE = """\
# ============================================================
# setup.ps1 - one-time environment setup for this site.
#   [1/4] Python venv + CMS Python dependencies
#   [2/4] npm install
#   [3/4] Prisma client
#   [4/4] Create SQLite database
# Run from the site root:  .\\setup.ps1
# (.env is auto-created by tools/sitegen/generate.py)
# ============================================================
$ErrorActionPreference = "Stop"

Write-Host "==> [1/4] Python venv + CMS dependencies"
$venvPy = ".\\venv\\Scripts\\python.exe"
if (-not (Test-Path $venvPy)) {
  Write-Host "    creating venv (first run can be slow)..."
  python -m venv venv
}
if (Test-Path $venvPy) {
  & $venvPy -m pip install --upgrade pip
  & $venvPy -m pip install -r .\\cms\\requirements.txt
  Write-Host "    CMS deps installed into venv"
} else {
  Write-Warning "    venv unavailable - installing CMS deps into system Python"
  python -m pip install --upgrade pip
  python -m pip install -r .\\cms\\requirements.txt
  Write-Host "    CMS deps installed into system Python"
}

Write-Host "==> [2/4] npm install"
npm install

Write-Host "==> [3/4] Prisma client"
npx prisma generate

Write-Host "==> [4/4] Create SQLite database"
npx prisma db push

Write-Host ""
Write-Host "Setup complete. Start developing with:  npm run dev"
Write-Host "CMS scripts use the venv Python:        .\\venv\\Scripts\\python.exe cms\\main.py"
"""


class GenError(Exception):
    """Fatal generator error with a user-facing message."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg):
    print(f"[sitegen] {msg}")


def load_json(path: Path) -> dict:
    if not path.exists():
        raise GenError(f"Missing file: {path}")
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise GenError(f"Invalid JSON in {path}: {exc}")
    if not isinstance(data, dict):
        raise GenError(f"{path} must be a JSON object")
    return data


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def write_json_i18n(path: Path, data):
    # Locale files ship with a UTF-8 BOM — preserve it so git diffs stay clean.
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def as_str(value) -> str:
    return "" if value is None else str(value)


def first_str(obj, *keys) -> str:
    for k in keys:
        if isinstance(obj, dict) and isinstance(obj.get(k), str) and obj.get(k):
            return obj[k]
    return ""


# ---------------------------------------------------------------------------
# 1. Manifest validation
# ---------------------------------------------------------------------------

def validate_company(company: dict) -> None:
    if not first_str(company, "name"):
        raise GenError("company.json: 'name' is required (full company name)")
    if not first_str(company, "shortName"):
        raise GenError("company.json: 'shortName' is required (brand used in titles/logo)")
    langs = company.get("languages")
    if langs is not None:
        if not isinstance(langs, list) or not langs or not all(isinstance(l, str) and l in LOCALE_META for l in langs):
            raise GenError(
                "company.json: 'languages' must be a non-empty array of "
                "supported codes (en, fr, de, es)"
            )
    default_locale = company.get("defaultLocale")
    if default_locale is not None:
        if default_locale not in LOCALE_META:
            raise GenError(f"company.json: 'defaultLocale' must be one of {list(LOCALE_META)}")
        langs = company.get("languages", DEFAULT_LANGUAGES)
        if default_locale not in langs:
            raise GenError("company.json: 'defaultLocale' must be listed in 'languages'")
    copy_overrides = company.get("copy")
    if copy_overrides is not None:
        if not isinstance(copy_overrides, dict):
            raise GenError("company.json: 'copy' must be an object keyed by locale (en/fr/de/es)")
        for loc in copy_overrides:
            if loc not in LOCALE_META:
                raise GenError(f"company.json: copy override key '{loc}' is not a supported locale")


# ---------------------------------------------------------------------------
# 2. Content validation
# ---------------------------------------------------------------------------

def validate_content(obj: dict, expected_type: str, lang: str) -> list:
    """Return a list of human-readable issues (empty = valid)."""
    issues = []
    meta = obj.get("meta")
    if not isinstance(meta, dict):
        issues.append("missing 'meta' object")
        meta = {}
    if obj.get("_type") not in (None, expected_type):
        issues.append(f"_type is '{obj.get('_type')}', expected '{expected_type}'")
    if not first_str(meta, "id"):
        issues.append("missing meta.id")
    if not first_str(meta, "status") or meta.get("status") not in ("draft", "published", "archived"):
        issues.append("meta.status must be draft|published|archived")
    overview = obj.get("overview")
    if not isinstance(overview, dict):
        issues.append("missing 'overview' object")
    else:
        if not first_str(overview, "title"):
            issues.append("missing overview.title")
        if not first_str(overview, "excerpt"):
            issues.append("missing overview.excerpt")
    if expected_type == "partner" and not first_str(meta, "type"):
        issues.append("partner: missing meta.type (e.g. company|institution|partner|consultant)")
    return issues


# ---------------------------------------------------------------------------
# 3. config.ts generation
# ---------------------------------------------------------------------------

def build_company_info(company: dict) -> dict:
    """Assemble the full companyInfo object for utils/config.ts."""
    default_copy = {
        "description": "{name} delivers professional services and tailored solutions to clients worldwide. "
                       "Contact us to discuss how we can help you achieve your goals."
    }

    def fill(text, **values):
        return text.format(**values)

    name = company["name"]
    short_name = company["shortName"]
    site_url = as_str(company.get("siteUrl")) or "https://www.yourdomain.com"
    host = re.sub(r"^https?://", "", site_url).rstrip("/")

    values = {
        "name": name,
        "shortName": short_name,
        "siteUrl": site_url,
        "host": host,
    }

    def fill_obj(val):
        if isinstance(val, str):
            return fill(val, **values)
        if isinstance(val, list):
            return [fill_obj(v) for v in val]
        if isinstance(val, dict):
            return {k: fill_obj(v) for k, v in val.items()}
        return val

    description = fill_obj(company.get("description") or default_copy["description"])
    external_links = company.get("externalLinks")
    if external_links is None:
        external_links = [
            {"name": "Example Partner", "url": "https://example.com"},
            {"name": "Industry Association", "url": "https://example.com"},
            {"name": "Case Studies", "url": "https://example.com"},
        ]
    social = company.get("socialLinks") or {}
    social = {
        "facebook": as_str(social.get("facebook")) or f"https://www.facebook.com/{short_name.lower()}",
        "twitter": as_str(social.get("twitter")) or f"https://twitter.com/{short_name.lower()}",
        "linkedin": as_str(social.get("linkedin")) or f"https://www.linkedin.com/company/{short_name.lower()}",
    }

    about = company.get("aboutPage") or {}
    about_page = {
        "statistics": about.get("statistics") or [
            {"value": "15+", "labelKey": "pages.about.stats.years"},
            {"value": "500+", "labelKey": "pages.about.stats.projects"},
            {"value": "98%", "labelKey": "pages.about.stats.satisfaction"},
            {"value": "120+", "labelKey": "pages.about.stats.clients"},
        ],
        "coreValues": about.get("coreValues") or [
            {"icon": "🎯", "titleKey": "pages.about.values.quality.title",
             "descriptionKey": "pages.about.values.quality.description"},
            {"icon": "🤝", "titleKey": "pages.about.values.trust.title",
             "descriptionKey": "pages.about.values.trust.description"},
            {"icon": "💡", "titleKey": "pages.about.values.transparency.title",
             "descriptionKey": "pages.about.values.transparency.description"},
        ],
        "teamMembers": about.get("teamMembers") or [
            {"initials": "ME", "nameKey": "pages.about.team.members.editorial.name",
             "roleKey": "pages.about.team.members.editorial.role",
             "bioKey": "pages.about.team.members.editorial.bio"},
            {"initials": "MT", "nameKey": "pages.about.team.members.leadership.name",
             "roleKey": "pages.about.team.members.leadership.role",
             "bioKey": "pages.about.team.members.leadership.bio"},
            {"initials": "CS", "nameKey": "pages.about.team.members.support.name",
             "roleKey": "pages.about.team.members.support.role",
             "bioKey": "pages.about.team.members.support.bio"},
        ],
        "reasons": about.get("reasons") or [
            {"titleKey": "pages.about.whyChooseUs.expertise.title",
             "descriptionKey": "pages.about.whyChooseUs.expertise.description"},
            {"titleKey": "pages.about.whyChooseUs.network.title",
             "descriptionKey": "pages.about.whyChooseUs.network.description"},
            {"titleKey": "pages.about.whyChooseUs.support.title",
             "descriptionKey": "pages.about.whyChooseUs.support.description"},
            {"titleKey": "pages.about.whyChooseUs.savings.title",
             "descriptionKey": "pages.about.whyChooseUs.savings.description"},
        ],
    }

    info = {
        "name": name,
        "shortName": short_name,
        "address": as_str(company.get("address")) or "Your street address, City, Country",
        "phone": as_str(company.get("phone")) or "+00 0000-0000",
        "email": as_str(company.get("email")) or "info@yourdomain.com",
        "workingHours": as_str(company.get("workingHours")) or "Monday to Friday: 9:00 - 18:00",
        "copyright": as_str(company.get("copyright")) or "All Rights Reserved",
        "year": as_str(company.get("year")) or "2026",
        "siteUrl": site_url,
        "description": description,
        "logoPath": as_str(company.get("logoPath")) or "/images/logo/logo.png",
        "externalLinks": fill_obj(external_links),
        "aboutPage": fill_obj(about_page),
        "socialLinks": fill_obj(social),
    }
    return info


def write_config_ts(repo: Path, info: dict) -> None:
    target = repo / "utils" / "config.ts"
    header = (
        "// AUTO-GENERATED by tools/sitegen/generate.py — do not edit manually.\n"
        "// Re-run the generator to apply changes from your input/company.json.\n\n"
    )
    body = "export const companyInfo = " + json.dumps(info, ensure_ascii=False, indent=2) + "\n"
    target.write_text(header + body, encoding="utf-8")
    log(f"wrote {target.relative_to(repo)}")


# ---------------------------------------------------------------------------
# 3b. site.config.json generation (nav + footer)
# ---------------------------------------------------------------------------

def build_site_config(company: dict) -> dict:
    """Assemble site.config.json from company.json. Falls back to template defaults
    for any section the user didn't provide, so partial configs still work."""
    default_nav = [
        {"to": "/", "labelKey": "nav.home"},
        {"to": "/products", "labelKey": "nav.products"},
        {"to": "/services", "labelKey": "nav.services"},
        {"to": "/partners", "labelKey": "nav.partners"},
        {"to": "/blogs", "labelKey": "nav.stories"},
        {"to": "/about", "labelKey": "nav.about"},
        {"to": "/contact", "labelKey": "nav.contact"},
    ]
    default_quick = [
        {"to": "/products", "labelKey": "footer.products"},
        {"to": "/services", "labelKey": "footer.ourServices"},
        {"to": "/partners", "labelKey": "footer.partners"},
        {"to": "/blogs", "labelKey": "nav.stories"},
        {"to": "/about", "labelKey": "footer.about"},
        {"to": "/contact", "labelKey": "footer.contact"},
    ]
    default_legal = [
        {"to": "/privacy", "labelKey": "footer.privacy"},
        {"to": "/terms", "labelKey": "footer.terms"},
        {"to": "/disclaimer", "labelKey": "footer.disclaimer"},
    ]

    nav = company.get("nav") or {}
    footer = company.get("footer") or {}
    return {
        "nav": {"items": nav.get("items") or default_nav},
        "footer": {
            "quickLinks": footer.get("quickLinks") or default_quick,
            "legalLinks": footer.get("legalLinks") or default_legal,
        },
    }


def write_site_config(repo: Path, company: dict) -> None:
    target = repo / "site.config.json"
    cfg = build_site_config(company)
    body = json.dumps(cfg, ensure_ascii=False, indent=2) + "\n"
    target.write_text(body, encoding="utf-8")
    log(f"wrote {target.relative_to(repo)}  (nav/footer from input/company.json)")


def build_deploy_config(company: dict, repo_name: str | None = None) -> dict:
    """Resolve the deploy workflow values, deriving sensible defaults from the
    output/repo directory name (i.e. the site's repo name). Falls back to the
    company manifest's shortName when no dir is given. All values are optional
    in input/company.json; an explicit "deploy" value always wins."""
    d = company.get("deploy") or {}
    base = repo_name or first_str(company, "shortName") or "site"
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-") or "site"

    def g(key, default):
        v = d.get(key)
        return as_str(v) if v not in (None, "") else default

    return {
        "enabled": bool(d.get("enabled", True)),
        "branch": g("branch", "main"),
        "nodeVersion": g("nodeVersion", "22"),
        "sshUser": g("sshUser", "ubuntu"),
        "runUser": g("runUser", "www"),
        "serverPath": g("serverPath", f"/www/wwwroot/{slug}"),
        "pm2Name": g("pm2Name", slug),
        "stagingPath": g("stagingPath", f"/tmp/{slug}-deploy"),
        "scpSource": g("scpSource", ".output,ecosystem.config.cjs"),
        "secretsHost": g("secretsHost", "SERVER_HOST"),
        "secretsKey": g("secretsKey", "SERVER_SSH_KEY"),
    }


def _to_snake(key: str) -> str:
    """camelCase -> SNAKE_CASE (e.g. nodeVersion -> NODE_VERSION)."""
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", key).upper()


def write_deploy_workflow(repo: Path, company: dict) -> None:
    """Generate .github/workflows/deploy.yml into the target site directory."""
    cfg = build_deploy_config(company, repo.name)
    if not cfg["enabled"]:
        log("deploy: disabled -> skipping .github/workflows/deploy.yml")
        return
    yml = DEPLOY_YAML_TEMPLATE
    for key, val in cfg.items():
        if key == "enabled":
            continue
        yml = yml.replace("__" + _to_snake(key) + "__", str(val))
    target = repo / ".github" / "workflows" / "deploy.yml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yml, encoding="utf-8")
    log(f"wrote {target.relative_to(repo)}  (deploy workflow from input/company.json)")


def write_setup_script(repo: Path) -> None:
    """Write setup.ps1 (one-time env setup: venv + CMS deps, npm install,
    Prisma client, SQLite database) into the target site directory."""
    target = repo / "setup.ps1"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(SETUP_PS1_TEMPLATE, encoding="utf-8")
    log(f"wrote {target.relative_to(repo)}  (one-time environment setup)")


def write_ecosystem(repo: Path, company: dict) -> None:
    """Rewrite PM2 app name + cwd in ecosystem.config.cjs to match the deploy
    workflow (name = pm2Name, cwd = serverPath from the deploy config)."""
    path = repo / "ecosystem.config.cjs"
    if not path.exists():
        log("ecosystem: ecosystem.config.cjs not found, skipping")
        return
    d = build_deploy_config(company, repo.name)
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"(?m)^(\s*name:\s*)'[^']*'",
        lambda m: m.group(1) + f"'{d['pm2Name']}'",
        text,
    )
    text = re.sub(
        r"(?m)^(\s*cwd:\s*)'[^']*'",
        lambda m: m.group(1) + f"'{d['serverPath']}'",
        text,
    )
    path.write_text(text, encoding="utf-8")
    log(f"updated {path.relative_to(repo)}  (pm2 name: {d['pm2Name']}, cwd: {d['serverPath']})")


def ensure_env(repo: Path, company: dict) -> None:
    """Create repo/.env from repo/.env.example if missing (never overwrites).

    Replaces the admin API key with a fresh random secret, sets
    NUXT_PUBLIC_SITE_URL from the manifest's siteUrl, and points NUXT_DATA_DIR
    at the site's data directory (<site>/data). Comments from .env.example are preserved.
    """
    target = repo / ".env"
    if target.exists():
        log("env: .env already exists (skipped)")
        return
    example = repo / ".env.example"
    if not example.exists():
        log("env: no .env.example found, skipping .env creation")
        return
    text = example.read_text(encoding="utf-8")
    text = text.replace(
        "NUXT_ADMIN_API_KEY=change-me-to-a-long-random-string",
        "NUXT_ADMIN_API_KEY=" + secrets.token_hex(24),
    )
    site_url = as_str(company.get("siteUrl")) or "https://www.yourdomain.com"
    text = text.replace(
        "NUXT_PUBLIC_SITE_URL=https://www.yourdomain.com",
        f"NUXT_PUBLIC_SITE_URL={site_url}",
    )
    text = re.sub(
        r"(?m)^NUXT_DATA_DIR=.*$",
        lambda m: "NUXT_DATA_DIR=" + str(repo / "data"),
        text,
    )
    target.write_text(text, encoding="utf-8")
    log(f"wrote {target.relative_to(repo)}  (generated from .env.example)")


def _read_env_value(path: Path, key: str) -> str:
    """Read a KEY=value line from an env file (ignores comments and quotes)."""
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        if k.strip() == key:
            return v.strip().strip('"').strip("'")
    return ""


def ensure_cms_env(repo: Path, company: dict) -> None:
    """Create cms/.env from cms/.env.example if missing (never overwrites).

    Fills BASE_URL + LANGUAGES from the manifest, and reuses values from the
    site's .env: REMOTE_API_KEY <- NUXT_ADMIN_API_KEY, CMS_DATA_DIR <- NUXT_DATA_DIR.
    """
    target = repo / "cms" / ".env"
    if target.exists():
        log("cms env: cms/.env already exists (skipped)")
        return
    example = repo / "cms" / ".env.example"
    if not example.exists():
        log("cms env: no cms/.env.example found, skipping cms/.env creation")
        return
    text = example.read_text(encoding="utf-8")
    site_url = as_str(company.get("siteUrl")) or "https://www.yourdomain.com"
    text = re.sub(r"(?m)^BASE_URL=.*$", f"BASE_URL={site_url}", text)
    langs = company.get("languages") or DEFAULT_LANGUAGES
    text = re.sub(r"(?m)^LANGUAGES=.*$", "LANGUAGES=" + ",".join(langs), text)
    admin_key = _read_env_value(repo / ".env", "NUXT_ADMIN_API_KEY")
    if admin_key:
        text = re.sub(r"(?m)^REMOTE_API_KEY=.*$", f"REMOTE_API_KEY={admin_key}", text)
    data_dir = _read_env_value(repo / ".env", "NUXT_DATA_DIR")
    if data_dir:
        text = re.sub(r"(?m)^CMS_DATA_DIR=.*$", lambda m: f"CMS_DATA_DIR={data_dir}", text)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    log(f"wrote {target.relative_to(repo)}  (generated from cms/.env.example)")


# ---------------------------------------------------------------------------
# 4. i18n injection (template injection — no LLM)
# ---------------------------------------------------------------------------

def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base (arrays replaced, nested dicts merged)."""
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def replace_placeholders(value, values: dict):
    if isinstance(value, str):
        for placeholder, key in PLACEHOLDER_REPLACEMENTS:
            value = value.replace(placeholder, values[key])
        return value
    if isinstance(value, list):
        return [replace_placeholders(v, values) for v in value]
    if isinstance(value, dict):
        return {k: replace_placeholders(v, values) for k, v in value.items()}
    return value


def inject_i18n(repo: Path, company: dict) -> None:
    locale_dir = repo / "i18n" / "locales"
    langs = company.get("languages", DEFAULT_LANGUAGES)
    copy_overrides = company.get("copy") or {}

    values = {
        "shortName": company["shortName"],
        "name": company["name"],
        "host": re.sub(r"^https?://", "", as_str(company.get("siteUrl")) or "").rstrip("/"),
    }

    for lang in langs:
        path = locale_dir / f"{lang}.json"
        if not path.exists():
            # Fall back to the template's en.json if a locale file is missing
            if lang == "en" or not (locale_dir / "en.json").exists():
                log(f"skip i18n: {lang}.json does not exist (create it to enable this language)")
                continue
            log(f"i18n: {lang}.json missing, falling back to en.json")
            base = load_json(locale_dir / "en.json")
            # Keep existing name of the target language file untouched
            base.setdefault("languages", {}).setdefault(lang, lang)
        else:
            base = load_json(path)

        merged = deep_merge(base, copy_overrides.get(lang) or {})
        merged = replace_placeholders(merged, values)
        # Ensure the language-name map is complete for every supported locale,
        # so the language switcher can show full names for all languages.
        lang_names = merged.setdefault("languages", {})
        for code, meta in LOCALE_META.items():
            lang_names[code] = meta["name"]
        write_json_i18n(path, merged)
        log(f"injected brand copy into i18n/locales/{lang}.json")


# ---------------------------------------------------------------------------
# 5. Content + assets
# ---------------------------------------------------------------------------

def copy_content(input_dir: Path, repo: Path) -> None:
    data_root = repo / "data"
    content_root = input_dir / "content"
    if not content_root.exists():
        log("no content/ directory — skipping content")
        return

    for entity_type, rel_dir in CONTENT_DIRS.items():
        type_dir = content_root / INPUT_FOLDER[entity_type]
        if not type_dir.exists():
            continue
        for lang_dir in sorted(p for p in type_dir.iterdir() if p.is_dir()):
            lang = lang_dir.name
            if lang not in LOCALE_META:
                log(f"skip unknown language folder: {INPUT_FOLDER[entity_type]}/{lang}")
                continue
            for file in sorted(lang_dir.glob("*.json")):
                obj = load_json(file)
                issues = validate_content(obj, entity_type, lang)
                if issues:
                    raise GenError(f"Invalid {entity_type} content {file.relative_to(input_dir)}:\n  - " + "\n  - ".join(issues))
                obj["_type"] = entity_type
                obj.setdefault("meta", {})["language"] = lang
                if entity_type == "service":
                    obj["meta"].setdefault("category", as_str(obj["meta"].get("category")))
                if entity_type == "partner":
                    obj["meta"].setdefault("type", as_str(obj["meta"].get("type")))
                if entity_type == "product":
                    category = as_str(obj.get("meta", {}).get("category")) or "general"
                    dest = data_root / rel_dir / category / lang / file.name
                else:
                    dest = data_root / rel_dir / lang / file.name
                write_json(dest, obj)
                log(f"content: {rel_dir}/{lang}/{file.name}")

    # Copy .gitkeep placeholders for empty language dirs of tracked skeleton
    for entity_type, rel_dir in CONTENT_DIRS.items():
        type_dir = content_root / INPUT_FOLDER[entity_type]
        if not type_dir.exists():
            continue
        for lang_dir in sorted(p for p in type_dir.iterdir() if p.is_dir()):
            lang = lang_dir.name
            if lang not in LOCALE_META:
                continue
            if entity_type == "product":
                for cat in ("general",):
                    dest_dir = data_root / rel_dir / cat / lang
                    dest_dir.mkdir(parents=True, exist_ok=True)
            else:
                dest_dir = data_root / rel_dir / lang
                dest_dir.mkdir(parents=True, exist_ok=True)


def copy_assets(input_dir: Path, repo: Path) -> None:
    assets_root = input_dir / "assets"
    if not assets_root.exists():
        log("no assets/ directory — skipping assets")
        return

    # Brand logo
    logo_src = assets_root / "logo"
    if logo_src.exists():
        logo_dst = repo / "public" / "images" / "logo"
        logo_dst.mkdir(parents=True, exist_ok=True)
        for f in sorted(logo_src.iterdir()):
            if f.is_file():
                shutil.copy2(f, logo_dst / f.name)
                log(f"logo: copied {f.name} -> public/images/logo/{f.name}")

    # Hero image(s) -> public/images/ (homepage LCP hero)
    # Put any file(s) here, e.g. hero-bg.webp (and optional -640/-1280/-1920 variants).
    hero_src = assets_root / "hero"
    if hero_src.exists():
        hero_dst = repo / "public" / "images"
        hero_dst.mkdir(parents=True, exist_ok=True)
        for f in sorted(hero_src.iterdir()):
            if f.is_file():
                shutil.copy2(f, hero_dst / f.name)
                log(f"hero: copied {f.name} -> public/images/{f.name}")

    # Content images
    data_assets = repo / "data" / "assets"
    for asset_type in ASSET_TYPES:
        type_root = assets_root / asset_type
        if not type_root.exists():
            continue
        if asset_type == "products":
            # products 按分类子目录组织: input/assets/products/{category}/{id}/*
            for cat_dir in sorted(p for p in type_root.iterdir() if p.is_dir()):
                for id_dir in sorted(p for p in cat_dir.iterdir() if p.is_dir()):
                    dest = data_assets / asset_type / cat_dir.name / id_dir.name
                    dest.mkdir(parents=True, exist_ok=True)
                    for f in sorted(id_dir.iterdir()):
                        if f.is_file():
                            shutil.copy2(f, dest / f.name)
                            log(f"asset: {asset_type}/{cat_dir.name}/{id_dir.name}/{f.name}")
        else:
            for id_dir in sorted(p for p in type_root.iterdir() if p.is_dir()):
                dest = data_assets / asset_type / id_dir.name
                dest.mkdir(parents=True, exist_ok=True)
                for f in sorted(id_dir.iterdir()):
                    if f.is_file():
                        shutil.copy2(f, dest / f.name)
                        log(f"asset: {asset_type}/{id_dir.name}/{f.name}")


def rewrite_asset_urls(input_dir: Path, repo: Path) -> None:
    """Rewrite cover/visual URLs that point to local asset files into /api/assets URLs."""
    assets_root = input_dir / "assets"
    if not assets_root.exists():
        return
    api_prefix = "/api/assets/"

    def is_local_filename(url: str) -> bool:
        return bool(url) and "/" not in url and not url.startswith("http")

    def rewrite(obj, asset_type, entity_id, category=None):
        if isinstance(obj, dict):
            for key, value in list(obj.items()):
                if isinstance(value, str) and is_local_filename(value):
                    if category is not None:
                        path = assets_root / INPUT_FOLDER[asset_type] / category / entity_id / value
                        prefix = f"{api_prefix}{INPUT_FOLDER[asset_type]}/{category}/{entity_id}"
                    else:
                        path = assets_root / INPUT_FOLDER[asset_type] / entity_id / value
                        prefix = f"{api_prefix}{INPUT_FOLDER[asset_type]}/{entity_id}"
                    if path.exists():
                        obj[key] = f"{prefix}/{value}"
                elif isinstance(value, (dict, list)):
                    rewrite(value, asset_type, entity_id, category)
        elif isinstance(obj, list):
            for item in obj:
                rewrite(item, asset_type, entity_id, category)

    data_root = repo / "data"
    for asset_type, rel_dir in CONTENT_DIRS.items():
        base = data_root / rel_dir
        if not base.exists():
            continue
        if asset_type == "product":
            # products: data/products/{category}/{lang}/*.json
            for cat_dir in sorted(p for p in base.iterdir() if p.is_dir()):
                for lang_dir in sorted(p for p in cat_dir.iterdir() if p.is_dir()):
                    if not lang_dir.is_dir():
                        continue
                    for file in lang_dir.glob("*.json"):
                        obj = load_json(file)
                        entity_id = as_str(obj.get("meta", {}).get("id"))
                        if not entity_id:
                            continue
                        rewrite(obj, asset_type, entity_id, category=cat_dir.name)
                        write_json(file, obj)
        else:
            for lang_dir in base.iterdir() if base.exists() else []:
                if not lang_dir.is_dir():
                    continue
                for file in lang_dir.glob("*.json"):
                    obj = load_json(file)
                    entity_id = as_str(obj.get("meta", {}).get("id"))
                    if not entity_id:
                        continue
                    rewrite(obj, asset_type, entity_id)
                    write_json(file, obj)


# ---------------------------------------------------------------------------
# 6. nuxt.config.ts locales sync
# ---------------------------------------------------------------------------

def sync_nuxt_locales(repo: Path, company: dict) -> None:
    langs = company.get("languages")
    if not langs:
        return
    cfg_path = repo / "nuxt.config.ts"
    text = cfg_path.read_text(encoding="utf-8")

    blocks = []
    for lang in langs:
        meta = LOCALE_META[lang]
        blocks.append(
            "      { \n"
            f"        code: '{lang}', \n"
            f"        iso: '{meta['iso']}', \n"
            f"        file: '{lang}.json',  // 相对于 i18n 目录\n"
            f"        name: '{meta['name']}' \n"
            "      }"
        )
    locale_block = "    locales: [\n" + ",\n".join(blocks) + "\n    ],"

    pattern = re.compile(r"    locales: \[[\s\S]*?\n    \],")
    if not pattern.search(text):
        log("nuxt.config.ts: could not find i18n.locales block — skipping (edit manually)")
        return
    text = pattern.sub(locale_block, text)
    cfg_path.write_text(text, encoding="utf-8")
    log(f"nuxt.config.ts: locales synced to {langs}")


# ---------------------------------------------------------------------------
# 7. Build
# ---------------------------------------------------------------------------

def run(cmd, repo: Path) -> None:
    log(f"$ {cmd}")
    proc = subprocess.run(cmd, cwd=str(repo), shell=True)
    if proc.returncode != 0:
        raise GenError(f"command failed: {cmd}")


def build_site(repo: Path, do_build: bool) -> None:
    if not do_build:
        return
    if not (repo / "node_modules").exists():
        run("npm install", repo)
    run("npx prisma generate", repo)
    run("npm run build", repo)


# ---------------------------------------------------------------------------
# Scaffold (--out)
# ---------------------------------------------------------------------------

def scaffold_repo(src: Path, dst: Path) -> Path:
    """Copy the template code skeleton into a NEW site directory.

    Excludes runtime/build artifacts, site content, and local env files, so the
    target is a clean, dev-ready Nuxt project. data/, .output/, node_modules/,
    .git/, .env, *.db, logs/, __pycache__ ... are all skipped; .env.example is kept.
    """
    if dst.exists() and any(dst.iterdir()):
        raise GenError(f"output directory not empty: {dst}")
    ignore = shutil.ignore_patterns(
        ".git", "node_modules", ".nuxt", ".nitro", ".data", ".output", "dist",
        "data", "input", "logs",
        "venv", ".venv", "__pycache__", "*.pyc", "*.pyo",
        ".env", "*.db", "*.db-journal",
        ".DS_Store",
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)
    log(f"scaffolded fresh site from template -> {dst}")
    return dst


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="MCA-CMS site generator")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="input directory (default: ./input)")
    parser.add_argument("--out", default=None,
                        help="scaffold a fresh site at this NEW directory (copy template code, "
                             "then inject content). Mutually exclusive with --repo.")
    parser.add_argument("--repo", default=str(DEFAULT_REPO), help="repo root (default: auto-detected)")
    parser.add_argument("--no-build", action="store_true", help="skip npm install/prisma/build")
    args = parser.parse_args()

    input_dir = Path(args.input).resolve()

    if args.out:
        repo = scaffold_repo(DEFAULT_REPO, Path(args.out).resolve())
    else:
        repo = Path(args.repo).resolve()

    if not input_dir.exists():
        log(f"input directory not found: {input_dir}")
        log("Start by copying tools/sitegen/input.example/ to ./input and filling it in.")
        return 1

    try:
        log(f"repo   : {repo}")
        log(f"input  : {input_dir}")

        # 1. Manifest
        company = load_json(input_dir / "company.json")
        validate_company(company)
        log(f"company: {company['name']} ({company['shortName']})")

        # 2. Optional tags override
        tags = input_dir / "tags.json"
        if tags.exists():
            tag_data = load_json(tags)
            if "tag_groups" not in tag_data:
                raise GenError("tags.json must contain a 'tag_groups' object (see config/tags.json)")
            shutil.copy2(tags, repo / "config" / "tags.json")
            log("tags.json -> config/tags.json")

        # 3. config.ts
        info = build_company_info(company)
        write_config_ts(repo, info)

        # 3b. site.config.json (nav + footer from input/company.json)
        write_site_config(repo, company)

        # 3c. deploy workflow (.github/workflows/deploy.yml)
        write_deploy_workflow(repo, company)

        # 3d. one-time environment setup script (setup.ps1)
        write_setup_script(repo)

        # 3d2. PM2 app name + cwd (matches deploy.yml)
        write_ecosystem(repo, company)

        # 3e. .env (from .env.example; random admin key, site URL, data dir)
        ensure_env(repo, company)

        # 3f. cms/.env (from cms/.env.example; BASE_URL for canonical/hreflang + sync)
        ensure_cms_env(repo, company)

        # 4. i18n injection
        inject_i18n(repo, company)

        # 5. Content + assets
        copy_content(input_dir, repo)
        copy_assets(input_dir, repo)
        rewrite_asset_urls(input_dir, repo)

        # 6. Locales sync
        sync_nuxt_locales(repo, company)

        # 7. Build
        build_site(repo, not args.no_build)

        log("DONE. Your site is ready: .output/ (deploy it with ecosystem.config.cjs)")
        return 0

    except GenError as exc:
        print(f"\n[sitegen] ERROR: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[sitegen] interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
