"""Copy provider JSON files from English to target language directories, updating language field."""
import json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings

base = settings.PROVIDER_OUTPUT_DIR
en_dir = base / 'en'
langs = ['ja', 'ko', 'ru']

for filename in os.listdir(en_dir):
    if not filename.endswith('.json'):
        continue
    src = os.path.join(en_dir, filename)
    with open(src, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for lang in langs:
        dst_dir = base / lang
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, filename)
        if not os.path.exists(dst):
            data['meta']['language'] = lang
            with open(dst, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Created: {lang}/{filename}")
        else:
            print(f"Skipped (exists): {lang}/{filename}")

print("Done!")
