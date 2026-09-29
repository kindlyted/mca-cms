import json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings

slug = 'dental-implants-china-cost'
langs = ['en', 'es', 'fr']
base = settings.BLOG_OUTPUT_DIR

print('=== FAQ comparison ===')
faqs = {}
for lang in langs:
    path = os.path.join(base, lang, f'{slug}.json')
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    faq = data.get('faq', [])
    faqs[lang] = faq
    print(f'\n--- {lang} ({len(faq)} items) ---')
    for i, item in enumerate(faq):
        q = item.get('q', '')
        print(f'  Q{i+1}: {q[:70]}')

# Check match
en_qs = [q['q'].lower().strip() for q in faqs['en']]
es_qs = [q['q'].lower().strip() for q in faqs['es']]
fr_qs = [q['q'].lower().strip() for q in faqs['fr']]

matches_es = 0
for eq in en_qs:
    for sq in es_qs:
        if eq[:25] == sq[:25] or eq[:25] in sq or sq[:25] in eq:
            matches_es += 1
            break

matches_fr = 0
for eq in en_qs:
    for fq in fr_qs:
        if eq[:25] == fq[:25] or eq[:25] in fq or fq[:25] in eq:
            matches_fr += 1
            break

print(f'\n=== 结论 ===')
print(f'EN→ES: {matches_es}/{len(en_qs)} 条问题大致匹配')
print(f'EN→FR: {matches_fr}/{len(en_qs)} 条问题大致匹配')
print(f'翻译一致吗？{"✅ 是" if matches_es == len(en_qs) and matches_fr == len(en_qs) else "❌ 否，不同语言FAQ不一样"}')
