# MCA-CMS Content Generator — Agent Guide

This directory is the **LLM-driven content generator** for the site. It produces
JSON content for the four entities (product / service / partner / blog) by
calling the **user's own LLM API** (OpenAI-compatible), and writes results
straight into `data/`. Use it when the user asks to generate site content.

For the human-facing manual, see `cms/README.md`.

## Working directory

Run every command from `cms/` (scripts use relative imports):

```powershell
cd c:\pyproj\mca-cms\cms
```

## Configuration (`cms/.env`, copy from `.env.example`)

At least one LLM provider is required (`llmcore.py` `PROVIDER_CONFIG`):

```env
API_KEY_DS=sk-xxx
URL_DS=https://api.deepseek.com/v1
# or API_KEY_ZHIPU/URL_ZHIPU, API_KEY_KIMI/URL_KIMI, API_KEY_QWEN/URL_QWEN
DEFAULT_PROVIDER=deepseek        # optional default provider
BASE_URL=https://www.yourdomain.com   # used for canonical/hreflang
```

`config/settings.py` holds: `LANGUAGES` (default en/fr/de), data dirs, image and
sync settings. LLM provider is chosen via `--provider` (default
`DEFAULT_PROVIDER`).

## CLI — `main.py`

```
.\venv\Scripts\python.exe cms\main.py <entity> ...     # generate content (run from site root)
.\venv\Scripts\python.exe cms\main.py validate --files <path...>
```

Common options on every generator: `--lang` (`en`/`fr`/`de`/`all`), `--id`,
`--slug`, `--provider`, `--sync`, `--style`, `--featured`.

| Command | Required | Generates |
|---------|----------|-----------|
| `blog --topic "..."` or `--md file.md` | topic or md | `data/blogs/{lang}/{slug}.json` |
| `service --name "..."` (or `--md`) | name or md | `data/services/{lang}/{slug}.json` |
| `provider --name "..."` (or `--md`) | name or md | `data/partners/{lang}/{slug}.json` (`_type: partner`) |
| `product --name "..."` | name | `data/products/{category}/{lang}/{slug}.json` |
| `validate --files ...` | files | schema check |

`--lang all` loops over `settings.LANGUAGES`. `--sync` pushes to the remote site
after generation (needs `REMOTE_API_URL`/`REMOTE_API_KEY` in `.env`).

### Translation — `translate.py`

Translates existing source-language JSON to other languages (preserves
structure/ids/slugs, rewrites text fields). Prefer this over regenerating when
the source language already exists.

```
python translate.py --entity blog --source-lang en                # all langs
python translate.py --entity service --slug my-svc --target-langs fr,de
python translate.py --entity product --source-lang en --provider deepseek
```

## Data output

| Entity | JSON path | Assets |
|--------|-----------|--------|
| blog | `data/blogs/{lang}/` | `data/assets/blogs/{id}/` |
| service | `data/services/{lang}/` | `data/assets/services/{id}/` |
| provider | `data/partners/{lang}/` (`_type: partner`) | `data/assets/partners/{id}/` |
| product | `data/products/{category}/{lang}/` | `data/assets/products/{category}/{id}/` |

## Hard rules when generating content

- **Never use `|` (pipe)** in any generated text — vue-i18n truncates at it. Use ` - `.
- JSON output must be **valid, no BOM, no markdown code fences** (`invoke_llm_json` strips ``` fences as a fallback, but keep output clean).
- Keep images ≈ ≤150 KB, prefer WebP.
- The generator overwrites the file for the same id (idempotent); it does not delete unrelated content.
- Internal name `provider` is emitted as `_type: partner` and routed to `/partners/`; `doctors` maps to mca `team`.
- Products are organised by `meta.category`: `data/products/{category}/{lang}`.

## Customising for a user's own entity

To change fields / add an entity, touch these in order:

1. `config/settings.py` — output/asset dirs, languages.
2. `generators/base.py` — `*_TEMPLATE` (the field schema) + add to `TEMPLATES`.
3. `generators/{entity}_generator.py` — `_assemble()` maps LLM output → fields.
4. `prompts/{entity}_content.prompt` — tells the LLM which fields to output.
5. `main.py` — import + subcommand. Optionally `_ROUTE_MAP` in `base.py` for
   canonical/hreflang route prefix (use plural for the route, singular `_type`).

## Optional integrations

- **Images**: `IMAGE_GENERATOR=ai` (Qwen/Seedream, needs `API_KEY_DASHSCOPE`/`API_KEY_ARK`) or `unsplash` (`UNP_AKEY`). Each generator also auto-generates a cover.
- **Web search (Tavily)**: blog generation fetches authoritative sources via `tavily_search.py` when `API_KEY_TAVILY` is set (and `pip install tavily-python`). No-op (skips search) when unconfigured — never fail.
- **Remote sync**: `sync_client.py` pushes to `POST /api/{type}` (blog/services/partners/products), uploads images to `/api/{type}/upload`, deletes via `DELETE /api/{type}/{id}`. `REMOTE_API_KEY` must equal the site's `NUXT_ADMIN_API_KEY`.
