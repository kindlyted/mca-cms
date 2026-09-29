"""Reset files that have incorrectly translated _type or country fields, then re-translate."""
import json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings

LANGUAGES = ['ja', 'ko', 'ru']
BASE = settings.DATA_DIR
SUBDIRS = [
    ('services', 'service'),
    ('partners', 'provider'),
]

en_texts = {}  # Cache English originals

for subdir, _ in SUBDIRS:
    en_dir = os.path.join(BASE, subdir, 'en')
    if not os.path.isdir(en_dir):
        continue
    
    for filename in os.listdir(en_dir):
        if not filename.endswith('.json'):
            continue
        
        en_path = os.path.join(en_dir, filename)
        with open(en_path, 'r', encoding='utf-8') as f:
            en_data = json.load(f)
        
        en_type = en_data.get('_type', '')
        
        for lang in LANGUAGES:
            dst_path = os.path.join(BASE, subdir, lang, filename)
            if not os.path.exists(dst_path):
                continue
            
            with open(dst_path, 'r', encoding='utf-8') as f:
                dst_data = json.load(f)
            
            dst_type = dst_data.get('_type', '')
            dst_country = dst_data.get('meta', {}).get('country', '')
            
            needs_reset = False
            if dst_type != en_type:
                print(f"Reset _type: {lang}/{filename} ('{dst_type}' → '{en_type}')")
                dst_data['_type'] = en_type
                needs_reset = True
            if dst_country != 'China':
                print(f"Reset country: {lang}/{filename} ('{dst_country}' → 'China')")
                dst_data['meta']['country'] = 'China'
                needs_reset = True
            
            if needs_reset:
                with open(dst_path, 'w', encoding='utf-8') as f:
                    json.dump(dst_data, f, ensure_ascii=False, indent=2)

print("\nReset complete!")
