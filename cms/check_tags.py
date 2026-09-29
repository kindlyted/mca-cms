"""Check tag usage across blogs vs config reference."""
import json, os, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings

used_tags = []
blog_dir = settings.BLOG_OUTPUT_DIR / 'en'
for f in os.listdir(blog_dir):
    if not f.endswith('.json'):
        continue
    with open(os.path.join(blog_dir, f), 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    tags = data.get('tags', {})
    for t in tags.get('primary', []):
        used_tags.append(('primary', t.get('id', ''), t.get('name', ''), t.get('group', '')))
    for t in tags.get('secondary', []):
        used_tags.append(('secondary', t.get('id', ''), t.get('name', ''), t.get('group', '')))

with open(settings.PROJECT_ROOT / 'config' / 'tags.json', 'r', encoding='utf-8') as fh:
    config_tags = json.load(fh)

config_ids = set()
config_names = {}
for gname, gdata in config_tags['tag_groups'].items():
    for tid, tinfo in gdata.items():
        if tid.startswith('_'):
            continue
        config_ids.add(tid)
        config_names[tid] = tinfo['name']

config_groups = {}
for gname, gdata in config_tags['tag_groups'].items():
    for tid in gdata:
        if tid.startswith('_'):
            continue
        config_groups[tid] = gname

# Tags in blog not in config
missing = [(tid, tg) for r, tid, nm, tg in used_tags if tid not in config_ids]
print(f'=== Tags NOT in config/tags.json ({len(missing)} instances) ===')
for tid, tg in sorted(set(missing)):
    print(f'  id="{tid}"  group="{tg}"')

# Tags with name mismatch vs config
print(f'\n=== Tags with name mismatch vs config/tags.json ===')
seen_names = set()
for r, tid, nm, tg in used_tags:
    if tid in config_names and config_names[tid] != nm:
        key = (tid, nm)
        if key not in seen_names:
            seen_names.add(key)
            print(f'  id="{tid}": blog name="{nm}"  vs  config name="{config_names[tid]}"')

# Unique tag IDs
unique_ids = set(t[1] for t in used_tags)
print(f'\n=== Summary ===')
print(f'Total tag instances in blogs: {len(used_tags)}')
print(f'Unique tag IDs used: {len(unique_ids)}')
print(f'In config/tags.json: {len(unique_ids & config_ids)}')
print(f'NOT in config/tags.json: {len(unique_ids - config_ids)}')
