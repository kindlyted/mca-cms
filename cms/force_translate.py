"""Force re-translate all service and provider files across all 3 languages."""
import json, os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings

BASE = settings.DATA_DIR
LANGUAGES = ['ja', 'ko', 'ru']
SUBDIRS = ['services', 'partners']
TRANSLATE_SCRIPT = str(Path(__file__).parent / 'batch_translate.py')
PYTHON = sys.executable

# Step 1: Set language to 'en' to force re-translate
count = 0
for subdir in SUBDIRS:
    for lang in LANGUAGES:
        dir_path = os.path.join(BASE, subdir, lang)
        if not os.path.isdir(dir_path):
            continue
        for filename in os.listdir(dir_path):
            if not filename.endswith('.json'):
                continue
            filepath = os.path.join(dir_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['meta']['language'] = 'en'
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            count += 1

print(f"Reset {count} files to language=en")

# Step 2: Run batch translation
result = subprocess.run(
    [PYTHON, TRANSLATE_SCRIPT],
    capture_output=True, text=True,
    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
)
print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[-500:])
