"""
Translate service JSON files from English to Japanese, Korean, and Russian.
Uses Deepseek provider via the existing CMS infrastructure.
"""
import json, os, sys, glob
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from llmcore import invoke_llm

EN_DIR = settings.SERVICE_OUTPUT_DIR / 'en'
LANGUAGES = {'ja': '日本語', 'ko': '한국어', 'ru': 'Русский'}

def get_english_texts(filepath):
    """Extract all translatable text fields from an English service JSON."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    texts = []
    
    def extract(obj, path=""):
        if isinstance(obj, str):
            texts.append((path, obj))
        elif isinstance(obj, dict):
            for k, v in obj.items():
                extract(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                extract(v, f"{path}[{i}]")
    
    extract(data)
    return data, texts

def translate_texts(texts, lang_name):
    """Use the configured LLM provider (llmcore) to translate all texts at once."""
    lines = [f"[{i}] {path}: {text}" for i, (path, text) in enumerate(texts)]
    batch_text = "\n".join(lines)
    
    prompt = f"""Translate the following medical tourism website texts to {lang_name}. 
Keep all {variable} placeholders unchanged. Keep brand names and proper nouns unchanged.
For medical terms, use standard {lang_name} medical terminology.

Return ONLY the translations, one per line in the same format: [INDEX]: TRANSLATED_TEXT

{batch_text}
"""
    
    try:
        result = invoke_llm("deepseek", prompt, temperature=0.3)
    except Exception as e:
        print(f"Translation error: {e}")
        return None
    
    translations = {}
    for line in result.strip().split('\n'):
        line = line.strip()
        if line.startswith('[') and ']: ' in line:
            idx = line[1:].split(']')[0]
            text = line.split(']: ', 1)[1]
            translations[int(idx)] = text
    
    return translations

def apply_translations(data, translations):
    """Apply translations back into the JSON structure."""
    def apply(obj, path="", idx=[0]):
        if isinstance(obj, str):
            if obj in [v for _, v in translations.items()]:
                pass  # handled at top level
            return obj
        elif isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                new_path = f"{path}.{k}" if path else k
                if isinstance(v, str) and new_path in [p for p, _ in texts]:
                    tidx = [p for p, _ in texts].index(new_path)
                    if tidx in translations:
                        result[k] = translations[tidx]
                    else:
                        result[k] = v
                else:
                    result[k] = apply(v, new_path, idx)
            return result
        elif isinstance(obj, list):
            result = []
            for i, v in enumerate(obj):
                new_path = f"{path}[{i}]"
                if isinstance(v, str) and new_path in [p for p, _ in texts]:
                    tidx = [p for p, _ in texts].index(new_path)
                    if tidx in translations:
                        result.append(translations[tidx])
                    else:
                        result.append(v)
                else:
                    result.append(apply(v, new_path, idx))
            return result
        return obj
    
    return apply(data)

def main():
    en_files = sorted(glob.glob(str(EN_DIR / '*.json')))
    print(f"Found {len(en_files)} English service files")
    
    for en_file in en_files:
        filename = os.path.basename(en_file)
        print(f"\nProcessing: {filename}")
        
        data, texts = get_english_texts(en_file)
        print(f"  Extracted {len(texts)} text fields")
        
        for lang_code, lang_name in LANGUAGES.items():
            out_dir = settings.SERVICE_OUTPUT_DIR / lang_code
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / filename
            
            if out_file.exists():
                print(f"  {lang_name}: skipping (already exists)")
                continue
            
            print(f"  Translating to {lang_name}...")
            translations = translate_texts(texts, lang_name)
            
            if translations is None:
                print(f"  {lang_name}: FAILED")
                continue
            
            # Apply translations and update language field
            translated_data = json.loads(json.dumps(data))  # deep copy
            translated_data['meta']['language'] = lang_code
            translated_data['meta']['author']['name'] = translations.get(
                next((i for i, (p, _) in enumerate(texts) if p == 'meta.author.name'), -1),
                data['meta']['author']['name']
            )
            translated_data['meta']['author']['role'] = translations.get(
                next((i for i, (p, _) in enumerate(texts) if p == 'meta.author.role'), -1),
                data['meta']['author']['role']
            )
            
            # Apply all other translations
            for path_idx, (path, _) in enumerate(texts):
                if path in ('meta.author.name', 'meta.author.role', 'meta.language'):
                    continue
                if path_idx in translations:
                    # Navigate to the right path and update
                    parts = path.split('.')
                    obj = translated_data
                    for part in parts[:-1]:
                        if '[' in part:
                            # Handle array index
                            arr_name, idx_str = part.split('[')
                            idx = int(idx_str.rstrip(']'))
                            obj = obj[arr_name][idx]
                        else:
                            obj = obj[part]
                    last_part = parts[-1]
                    if last_part in obj:
                        obj[last_part] = translations[path_idx]
            
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(translated_data, f, ensure_ascii=False, indent=2)
            
            print(f"  {lang_name}: ✓ ({len(translations)} translations applied)")
    
    print("\nDone!")

if __name__ == '__main__':
    main()
