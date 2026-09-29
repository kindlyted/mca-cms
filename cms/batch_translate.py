"""
Batch translate service and provider JSON content from English to ja, ko, ru.
Uses DeepSeek API via existing CMS infrastructure.
"""
import json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from llmcore import invoke_llm

LANGUAGES = {
    'ja': ('Japanese', 'natural Japanese (です/ます体)'),
    'ko': ('Korean', 'formal polite Korean (존댓말)'),
    'ru': ('Russian', 'natural Russian'),
}

DATA_DIR = settings.DATA_DIR
BATCHES = [
    ('services', 'service'),
    ('partners', 'provider'),
]

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
            new_path = f"{path}[{i}]"
            texts.extend(extract_text_fields(v, new_path, skip_paths))
    return texts

def set_nested_value(obj, path, value):
    """Set a value in a nested dict/list structure using dot notation path."""
    parts = path.split('.')
    current = obj
    for i, part in enumerate(parts[:-1]):
        if '[' in part:
            # Handle array[index]
            arr_name = part[:part.index('[')]
            idx = int(part[part.index('[')+1:part.index(']')])
            current = current[arr_name][idx]
        else:
            current = current[part]
    
    last = parts[-1]
    if '[' in last:
        arr_name = last[:last.index('[')]
        idx = int(last[last.index('[')+1:last.index(']')])
        current[arr_name][idx] = value
    else:
        current[last] = value

def translate_batch(texts, lang_name, lang_desc, retries=3):
    """Translate a batch of texts using the configured LLM provider (llmcore)."""
    lines = [f"[{i}] {text}" for i, (_, text) in enumerate(texts)]
    batch = "\n".join(lines)
    
    prompt = f"""Translate the following medical tourism website texts to {lang_desc}.

Rules:
- Keep ALL {{variable}} placeholders untouched (e.g. {{from}}, {{total}}, {{email}}, {{phone}}, etc.)
- Keep ALL brand names and proper nouns unchanged
- Keep URLs and image paths unchanged
- For medical terms, use standard {lang_name} medical terminology
- Preserve markdown formatting (**, #, -, |, etc.)
- Keep numbers and prices as-is

Return ONLY the translations, one per line in format: [INDEX]: TRANSLATED_TEXT
Do NOT include any explanations or comments.

{batch}"""
    
    for attempt in range(retries):
        try:
            result = invoke_llm("deepseek", prompt, temperature=0.3).strip()
            
            translations = {}
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('[') and ']: ' in line:
                    try:
                        idx_str = line[1:line.index(']')]
                        idx = int(idx_str)
                        colon_pos = line.index(']: ')
                        text = line[colon_pos + 3:]
                        translations[idx] = text
                    except (ValueError, IndexError):
                        continue
            
            if len(translations) >= len(texts) * 0.7:
                return translations
            
            if attempt < retries - 1:
                print(f"    Only got {len(translations)}/{len(texts)} translations, retrying...")
                time.sleep(2)
        except Exception as e:
            print(f"    API error: {e}, retrying ({attempt+1}/{retries})...")
            time.sleep(3)
    
    return {}

def process_file(en_path, lang_code, lang_name, lang_desc):
    """Process a single file for one language."""
    rel_dir = en_path.parent.parent.name  # e.g. 'services' or 'providers'
    parent_dir = en_path.parent.parent
    filename = en_path.name
    
    dst_path = parent_dir / lang_code / filename
    
    if not dst_path.exists():
        print(f"    {lang_name}: SKIP (no source file)")
        return False
    
    with open(en_path, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    
    with open(dst_path, 'r', encoding='utf-8') as f:
        dst_data = json.load(f)
    
    # Check if already translated (not just copied)
    # If language field matches and text content differs from English, skip
    is_already_translated = False
    if dst_data.get('meta', {}).get('language') == lang_code:
        en_title = en_data.get('overview', {}).get('title', '')
        dst_title = dst_data.get('overview', {}).get('title', '')
        # Also check _type field to detect partial translations
        en_type = en_data.get('_type', '')
        dst_type = dst_data.get('_type', '')
        if dst_title != en_title and dst_type == en_type:
            is_already_translated = True
    
    if is_already_translated:
        print(f"    {lang_name}: SKIP (already translated)")
        return True
    
    # Extract translatable text fields (skip meta.language, fields like id/slug/url)
    skip_paths = {'_type', 'meta.language', 'meta.id', 'meta.slug', 'meta.region', 'meta.country',
                   'meta.type', 'meta.city', 'meta.status', 'meta.difficulty', 'meta.duration', 'meta.priceRange',
                   'meta.author.id', 'meta.author.url', 'meta.createdAt', 'meta.updatedAt',
                   'meta.featured', 'meta.priority', 'meta.readTime'}
    
    texts = extract_text_fields(en_data, skip_paths=skip_paths)
    # Filter out non-text fields (containing only numbers, URLs, dates)
    filtered_texts = []
    for path, text in texts:
        if not isinstance(text, str) or not text.strip():
            continue
        if text.startswith('http') or text.startswith('/api/'):
            continue
        if text in ('check', 'Varies', 'Free', 'easy', 'published'):
            continue
        # Skip fields that are just identifiers
        if path.endswith('.id') or path.endswith('.url') or path.endswith('.icon'):
            continue
        filtered_texts.append((path, text))
    
    print(f"    {lang_name}: translating {len(filtered_texts)} text fields...")
    
    translations = translate_batch(filtered_texts, lang_name, lang_desc)
    
    if not translations:
        print(f"    {lang_name}: FAILED (no translations)")
        return False
    
    # Apply translations
    dst_data['meta']['language'] = lang_code
    
    for idx, (path, _) in enumerate(filtered_texts):
        if idx in translations:
            set_nested_value(dst_data, path, translations[idx])
    
    with open(dst_path, 'w', encoding='utf-8') as f:
        json.dump(dst_data, f, ensure_ascii=False, indent=2)
    
    print(f"    {lang_name}: ✓ ({len(translations)}/{len(filtered_texts)} fields translated)")
    return True

def main():
    total_files = 0
    total_success = 0
    
    for subdir, entity_type in BATCHES:
        en_dir = DATA_DIR / subdir / 'en'
        if not en_dir.exists():
            print(f"Directory not found: {en_dir}")
            continue
        
        files = sorted(en_dir.glob('*.json'))
        print(f"\n{'='*60}")
        print(f"Processing {len(files)} {entity_type} files")
        print(f"{'='*60}")
        
        for en_file in files:
            print(f"\n📄 {en_file.name}")
            total_files += 1
            file_ok = True
            
            for lang_code, (lang_name, lang_desc) in LANGUAGES.items():
                ok = process_file(en_file, lang_code, lang_name, lang_desc)
                if not ok:
                    file_ok = False
            
            if file_ok:
                total_success += 1
                print(f"  ✅ {en_file.name} completed")
            else:
                print(f"  ❌ {en_file.name} partially failed")
    
    print(f"\n{'='*60}")
    print(f"Done! {total_success}/{total_files} files processed successfully.")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
