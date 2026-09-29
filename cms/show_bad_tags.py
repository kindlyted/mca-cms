"""Show examples of non-standard tags in blog files."""
import json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings

blog_dir = settings.BLOG_OUTPUT_DIR / 'en'
config_path = settings.PROJECT_ROOT / 'config' / 'tags.json'

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

config_ids = set()
for gname, gdata in config['tag_groups'].items():
    for tid in gdata:
        if not tid.startswith('_'):
            config_ids.add(tid)

# Show 3 examples with non-standard tags
count = 0
for fname in sorted(os.listdir(blog_dir)):
    if not fname.endswith('.json'):
        continue
    with open(os.path.join(blog_dir, fname), 'r', encoding='utf-8') as f:
        data = json.load(f)
    tags = data.get('tags', {})
    bad_tags = []
    for t in tags.get('primary', []) + tags.get('secondary', []):
        if t['id'] not in config_ids:
            bad_tags.append(t)
    if bad_tags and count < 4:
        print(f'📄 {fname}')
        print(f'  Title: {data["overview"]["title"]}')
        for t in bad_tags:
            print(f'  ⚠️  id="{t["id"]}"  name="{t["name"]}" group="{t["group"]}')
        print()
        count += 1

# Also show a standard one
print('--- 标准tags的例子 ---')
with open(os.path.join(blog_dir, 'dental-implants-china-cost.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)
for t in data.get('tags', {}).get('primary', []):
    print(f'  ✅ id="{t["id"]}"  name="{t["name"]}"')
