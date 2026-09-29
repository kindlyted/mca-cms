"""
translate.py — Translate existing content JSON from one language to others.

Unlike regenerating with the generators, this translates the already-produced
source-language JSON in place, preserving structure / ids / slugs / URLs and
only rewriting the translatable text fields. Uses the same LLM provider as the
generators (llmcore), so you configure it once in cms/.env.

Usage:
    # Translate a single entity's existing files to all settings.LANGUAGES
    python translate.py --entity service --source-lang en

    # Translate one specific file
    python translate.py --entity blog --slug my-post --source-lang en --target-langs fr,de

    # Translate with a specific provider
    python translate.py --entity product --source-lang en --provider deepseek
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from llmcore import invoke_llm

# entity -> (output dir under DATA_DIR, asset prefix for skip)
ENTITY_DIRS = {
    "blog": "blogs",
    "service": "services",
    "provider": "partners",
    "product": "products",
}

# Fields that are structural / non-translatable.
SKIP_PATHS = {
    "_type", "meta.language", "meta.id", "meta.slug", "meta.region", "meta.country",
    "meta.type", "meta.city", "meta.status", "meta.difficulty", "meta.duration",
    "meta.priceRange", "meta.author.id", "meta.author.url", "meta.createdAt",
    "meta.updatedAt", "meta.featured", "meta.priority", "meta.readTime", "meta.category",
    "meta.country", "meta.publishedAt", "meta.updatedAt",
}


def extract_text_fields(obj, path="", skip_paths=None):
    """Extract all translatable text fields from a JSON object."""
    if skip_paths is None:
        skip_paths = set()
    texts = []
    if isinstance(obj, str):
        return [(path, obj)] if path not in skip_paths else []
    elif isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            texts.extend(extract_text_fields(v, new_path, skip_paths))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            texts.extend(extract_text_fields(v, f"{path}[{i}]", skip_paths))
    return texts


def set_nested_value(obj, path, value):
    """Set a value in a nested dict/list structure using dot-notation path."""
    parts = path.split(".")
    current = obj
    for i, part in enumerate(parts[:-1]):
        if "[" in part:
            arr_name = part[:part.index("[")]
            idx = int(part[part.index("[") + 1:part.index("]")])
            current = current[arr_name][idx]
        else:
            current = current[part]
    last = parts[-1]
    if "[" in last:
        arr_name = last[:last.index("[")]
        idx = int(last[last.index("[") + 1:last.index("]")])
        current[arr_name][idx] = value
    else:
        current[last] = value


def filter_texts(texts):
    """Drop fields that are not real translatable prose."""
    out = []
    for path, text in texts:
        if not isinstance(text, str) or not text.strip():
            continue
        if text.startswith("http") or text.startswith("/api/"):
            continue
        if text in ("check", "Varies", "Free", "easy", "published"):
            continue
        if path.endswith(".id") or path.endswith(".url") or path.endswith(".icon"):
            continue
        out.append((path, text))
    return out


def translate_texts(texts, lang_name, provider, retries=3):
    """Translate a batch of texts via llmcore (OpenAI-compatible, user's provider)."""
    lines = [f"[{i}] {text}" for i, (_, text) in enumerate(texts)]
    batch = "\n".join(lines)

    user_input = (
        f"Translate the following website texts to {lang_name}.\n\n"
        "Rules:\n"
        "- Keep ALL {variable} placeholders untouched (e.g. {from}, {total}, {email}).\n"
        "- Keep URLs, image paths, brand names and proper nouns unchanged.\n"
        "- Preserve markdown formatting (**, #, -, |).\n"
        "- Keep numbers and prices as-is.\n"
        "- Return ONLY the translations, one per line: [INDEX]: TRANSLATED_TEXT\n"
        "- Do NOT add explanations.\n\n"
        f"{batch}"
    )

    for attempt in range(retries):
        try:
            response = invoke_llm(provider, user_input, temperature=0.3)
            result = response.strip()
            translations = {}
            for line in result.split("\n"):
                line = line.strip()
                if line.startswith("[") and "]: " in line:
                    try:
                        idx = int(line[1:line.index("]")])
                        text = line[line.index("]: ") + 3:]
                        translations[idx] = text
                    except (ValueError, IndexError):
                        continue
            if len(translations) >= len(texts) * 0.7:
                return translations
            print(f"    Only {len(translations)}/{len(texts)}, retrying...")
            time.sleep(2)
        except Exception as e:
            print(f"    API error: {e}, retrying ({attempt + 1}/{retries})...")
            time.sleep(3)
    return {}


def process_file(en_path, lang_code, lang_name, provider):
    """Translate a single source file into one target language."""
    entity_dir = en_path.parent.parent  # e.g. data/services (or data/products/{cat})
    filename = en_path.name
    dst_path = entity_dir / lang_code / filename

    if not dst_path.exists():
        print(f"    {lang_code}: SKIP (no existing target file)")
        return False

    en_data = json.loads(en_path.read_text(encoding="utf-8"))
    dst_data = json.loads(dst_path.read_text(encoding="utf-8"))

    # Skip if already translated (target title differs from source and same _type)
    if dst_data.get("meta", {}).get("language") == lang_code:
        if dst_data.get("overview", {}).get("title") != en_data.get("overview", {}).get("title") \
                and dst_data.get("_type") == en_data.get("_type"):
            print(f"    {lang_code}: SKIP (already translated)")
            return True

    texts = filter_texts(extract_text_fields(en_data, skip_paths=SKIP_PATHS))
    if not texts:
        return True

    print(f"    {lang_code}: translating {len(texts)} fields...")
    translations = translate_texts(texts, lang_name, provider)
    if not translations:
        print(f"    {lang_code}: FAILED")
        return False

    dst_data["meta"]["language"] = lang_code
    for idx, (path, _) in enumerate(texts):
        if idx in translations:
            set_nested_value(dst_data, path, translations[idx])

    dst_path.write_text(json.dumps(dst_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"    {lang_code}: OK ({len(translations)}/{len(texts)} fields)")
    return True


def main():
    parser = argparse.ArgumentParser(description="Translate existing CMS content JSON")
    parser.add_argument("--entity", required=True, help="blog | service | provider | product")
    parser.add_argument("--slug", help="Specific slug; omit to process all files")
    parser.add_argument("--source-lang", default="en", help="Source language (default en)")
    parser.add_argument("--target-langs", default=None, help="Comma list, e.g. fr,de (default: all settings.LANGUAGES)")
    parser.add_argument("--provider", default=None, help="LLM provider (default settings.DEFAULT_PROVIDER)")
    args = parser.parse_args()

    entity = args.entity
    if entity not in ENTITY_DIRS:
        print(f"Unknown entity: {entity}. Use {list(ENTITY_DIRS)}")
        sys.exit(1)

    provider = args.provider or settings.DEFAULT_PROVIDER
    target_langs = [l.strip() for l in args.target_langs.split(",")] if args.target_langs else \
        [l for l in settings.LANGUAGES if l != args.source_lang]

    # Resolve source directory (products are category-nested)
    if entity == "product":
        base = settings.PRODUCT_OUTPUT_BASE
        en_files = []
        for cat in base.iterdir() if base.exists() else []:
            if cat.is_dir():
                en_files.extend(sorted((cat / args.source_lang).glob("*.json")))
    else:
        base = settings.DATA_DIR / ENTITY_DIRS[entity]
        en_dir = base / args.source_lang
        en_files = sorted(en_dir.glob("*.json")) if en_dir.exists() else []

    if args.slug:
        en_files = [f for f in en_files if f.stem == args.slug]

    if not en_files:
        print(f"No source files found for {entity}/{args.source_lang}")
        sys.exit(1)

    lang_names = {"en": "English", "fr": "French", "de": "German"}
    ok = fail = 0
    for en_file in en_files:
        print(f"\n📄 {en_file.relative_to(settings.DATA_DIR)}")
        for lang in target_langs:
            if process_file(en_file, lang, lang_names.get(lang, lang), provider):
                ok += 1
            else:
                fail += 1

    print(f"\nDone. {ok} ok, {fail} failed.")


if __name__ == "__main__":
    main()
