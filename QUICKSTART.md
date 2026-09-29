# Quick Start — From Template to Deployed Site

This is the **single onboarding document**. You provide four things, run one
command, and get a fully built site. It works like WordPress: you fill in
data, the script assembles the site, and you deploy the result.

The site generator lives at `tools/sitegen/generate.py` (`npm run sitegen`).
This guide is its manual — there is no separate README.

## 0. What you prepare (checklist)

### Customize (edit files yourself)

| Item | Where |
|------|-------|
| **logo** | `input/assets/logo/` |
| **hero image** | `input/assets/hero/` (copied to `public/images/` as-is) |
| **nav / footer links** *(optional)* | `input/company.json` → `nav` / `footer` (generate.py writes `site.config.json`; omit to keep the standard navigation) |
| **Company info** | `input/company.json` |
| **Languages** | `input/company.json` → `languages` |

### Generate with an LLM

| Item | Where |
|------|-------|
| **Legal trio** (privacy / terms / disclaimer) | copy into `i18n/locales/*.json` → `legal.*` |
| **Tags dictionary** | `input/tags.json` (optional, overrides `config/tags.json`) |
| **i18n copy** | per-language in `input/content/{type}/{lang}/` + `company.json` → `copy` |

### Check before you ship

`/sitemap.xml`, `/robots.txt`, `/llms.txt` — they are generated automatically at
runtime, but verify they list your pages after the first build.

## The 4-step process

### Step 1 — Fill in the manifest

```powershell
Copy-Item tools/sitegen/input.example input -Recurse
# edit input/company.json — name and shortName are the essentials
```

`company.json` carries every structural value: brand name, tagline, contact,
statistics, core values, team members, **languages**, and optional per-language
`copy` overrides for the marketing prose. If you skip `copy`, the built-in
neutral template copy is used and only the brand placeholders are replaced.
`siteUrl` is **optional** — if omitted it defaults to `https://www.yourdomain.com`.
An optional `deploy` block configures the generated GitHub Actions workflow
(server path, PM2 name, …) — everything except `name`/`shortName` has a
sensible default, so a minimal manifest only needs those two.

### Step 2 — Drop in your content

Put one JSON file per product / service / partner / article into
`input/content/{products|services|partners|blogs}/{lang}/`, and repeat the same
files for every language in your `company.json` `languages` array.

Required per file:
- `meta.id` — unique id (used for the filename and URLs)
- `meta.status` — `"published"` to show it
- `overview.title`, `overview.excerpt`
- partners also need `meta.type`
- products may add `meta.category` (defaults to `general`) to organise the
  sub-folder under `data/products/{category}/{lang}/`

Everything else (pricing, process, FAQ, institution details, gallery, tags) is
optional — the schema lives in `server/schemas/content.ts` and the site renders
gracefully with partial data. Only use the folders your site actually needs.

### Step 3 — Generate

**Brand-new site (one command — recommended):**

```powershell
python tools/sitegen/generate.py --input input/ --out my-site
```

This scaffolds a clean Nuxt skeleton into `my-site/` (no `node_modules`,
`data/`, `.git`, …), injects your content, generates
`.github/workflows/deploy.yml` + `setup.ps1`, and builds `.output/`. The
template repo itself is left untouched — `my-site` is the new independent site.

> **Naming matters.** The `--out` directory name (= the site's repo name) drives
> the deployment defaults: PM2 app name, server path `/www/wwwroot/<name>`, and
> staging path `/tmp/<name>-deploy` (also written into `ecosystem.config.cjs`).
> `shortName` is only the fallback when generating in place without `--out`.
> And `siteUrl` (your domain) feeds `NUXT_PUBLIC_SITE_URL` + `cms` `BASE_URL`
> (canonical/hreflang). So: pick the directory name to match the PM2/server
> name you want, keep `siteUrl` correct — everything else follows.

**Existing site (generate in place):**

```powershell
python tools/sitegen/generate.py          # or: npm run sitegen
# or:  python tools/sitegen/generate.py --no-build   (only generate, don't build)
```

The script validates everything, writes `utils/config.ts` + `site.config.json`,
generates `.github/workflows/deploy.yml` + `setup.ps1`, creates `.env` (random
admin key, your site URL, data dir, `DATABASE_URL`) and `cms/.env` (`BASE_URL`,
`LANGUAGES`, `REMOTE_API_KEY`, `CMS_DATA_DIR`), injects brand copy into
`i18n/locales/*.json`, copies content into `data/`, copies images and rewrites
asset URLs, syncs `nuxt.config.ts` locales, then runs
`npx prisma generate` + `npm run build`.

You now have `.output/` — a complete, built site. The script is idempotent:
re-running regenerates the generated files from the current manifest, but does
**not** delete content you placed in `data/` manually.

### Step 4 — Set up local env & deploy

**Local environment:** `.env` and `cms/.env` are created automatically by
`generate.py` (admin key, site URL, data dir, `DATABASE_URL`, and cms
`BASE_URL` / `LANGUAGES` / `REMOTE_API_KEY` / `CMS_DATA_DIR`). Run the setup
script once for the remaining one-time steps — Python venv with CMS deps,
`npm install`, Prisma client, SQLite DB:

```powershell
cd my-site
.\setup.ps1
```

**To a server** (recommended flow):
1. Fill the optional `deploy` block in `input/company.json` (server path, PM2
   name, …). Defaults derive from the site/repo name, so often nothing to
   change — `generate.py` writes `.github/workflows/deploy.yml` for you.
2. In the site's GitHub repo, add secrets: `SERVER_HOST` and `SERVER_SSH_KEY`
   (the generated workflow references them).
3. Upload `ecosystem.config.cjs`, `.env` and `prisma/` to the server (adjust
   PM2 `cwd` and app `name`).
4. On the server, run `npx prisma db push` once to create the SQLite DB.
5. Push to `main` → the action deploys. If content is deployed separately, set
   `NUXT_DATA_DIR` to the `data/` folder so both content and images resolve.

## CMS content generator (optional)

The repo ships a bundled **LLM-driven content generator** in `cms/` (Python CLI). It uses **your own LLM API** (DeepSeek / Zhipu / Kimi / Qwen / etc.) to generate JSON content for all four entity types (products / services / partners / blogs) and writes them straight into `data/`.

```powershell
# cms/.env is auto-created by generate.py (BASE_URL/LANGUAGES pre-filled);
# just add at least one LLM API key, then run from the site root (no activate needed):
.\venv\Scripts\python.exe cms\main.py product --name "large exercise mat" -l en
```

It also supports AI image generation, multi-language translation and remote sync. **Full usage + how to customise the generators for your own entities, see `cms/README.md`.**

## Verification

```powershell
npm run dev     # browse http://localhost:3000 and check all pages in all languages
```

If a page looks incomplete, that's a content issue — add the missing fields in
the corresponding `input/content/...` JSON and re-run the generator.

## Testing the template itself (and syncing with derived sites)

This repo is the **template**. Real sites are created by copying it out and
running the generator. Two concerns come up when you do that:

### 1. Smoke-test the template before shipping changes

The template ships with **sample content** in `tools/sitegen/input.example/`
(one product, one service, one partner, one blog, plus images and a filled-in
`company.json`). Use it as a throwaway input to exercise every page:

```powershell
Copy-Item tools/sitegen/input.example input -Recurse
python tools/sitegen/generate.py --no-build   # generate content only, skip build
npm run dev                                    # browse http://localhost:3000
```

Walk this checklist:

- All four listing pages open and filter/search/paginate: `/products`,
  `/services`, `/partners`, `/blogs`
- Each detail page renders fully: `/products/[slug]`, `/services/[slug]`, …
- Language switch `en / fr / de` works on every page
- Header/footer follow `site.config.json` (add/remove/reorder a nav item)
- Homepage sections, contact form, legal pages (`/privacy`, `/terms`, …)
- `/sitemap.xml`, `/robots.txt`, `/llms.txt`
- No blank pages and no console errors in the browser

When done, remove the throwaway input so the template stays clean:

```powershell
Remove-Item input -Recurse -Force
```

### 2. Sync code between the template and a derived site

A derived site mixes **template code** (`pages/`, `components/`, `server/`, …)
with **site content** (`data/`, `input/`, generated `utils/config.ts`, brand
injected into `i18n/locales/*.json`). So you can't copy whole files back and
forth blindly.

Use `tools/template_sync.py` to sync **only the template-code files**, either
direction, with a dry-run preview by default:

```powershell
# A) A fix was made in the derived site -> bring it back into the template
python tools/template_sync.py --to-template PATH\TO\SITE            # preview
python tools/template_sync.py --to-template PATH\TO\SITE --apply    # actually copy

# B) Template has updates -> push them into a derived site
python tools/template_sync.py --to-site PATH\TO\SITE --apply
```

Notes:

- **Dry-run by default** — review the file list, then re-run with `--apply`.
- Only files listed in `TEMPLATE_CODE` (in the script) are ever synced;
  `data/`, `input/`, build artifacts, `.env`, and `node_modules/` are always
  ignored.
- **Half-generated files** (`utils/config.ts`, `nuxt.config.ts`,
  `site.config.json`, `i18n/locales/*.json`) are skipped unless you pass
  `--include-generated`,
  and even then treat them as needing manual review — they carry site-specific
  brand/localized data that a blind overwrite would clobber.
- Add new template-code paths to `TEMPLATE_CODE` in the script when you add
  directories that should flow between template and sites.

## Notes for LLM-assisted content generation

When you have a model generate content for this CMS, tell it:

- **Never use `|` (pipe)** in any locale value — vue-i18n truncates at `|`.
  Use ` - ` instead.
- **Never write JSON with a BOM** (the generator writes locale files with a BOM
  on purpose to keep git diffs clean; generated content files should be plain
  UTF-8).
- **Keep images ≈ ≤150 KB** and prefer WebP.

---

## Appendix — sitegen input reference

### Input folder

```
input/
  company.json              REQUIRED — site manifest (see below)
  tags.json                 OPTIONAL — override of config/tags.json (same shape)
  content/
    products/{lang}/*.json  product pages       (按 meta.category 分目录)
    services/{lang}/*.json  service pages        (one file per service)
    partners/{lang}/*.json  partner pages        (one file per partner)
    blogs/{lang}/*.json     blog articles        (one file per article)
  assets/
    logo/logo.png           → public/images/logo/
    hero/hero-bg.webp       → public/images/ (copied as-is; add -640/-1280/-1920 variants for responsive)
    products/{cat}/{id}/*   → data/assets/products/{cat}/{id}/
    services/{id}/*         → data/assets/services/{id}/
    partners/{id}/*         → data/assets/partners/{id}/
    blogs/{id}/*            → data/assets/blogs/{id}/
```

### company.json — fields

| Field | Required | Notes |
|-------|----------|-------|
| `name` | ✅ | Full company name (footer, meta, about) |
| `shortName` | ✅ | Brand used in page titles / logo. Fallback for PM2/server names when generating in place (no `--out`) |
| `siteUrl` | | **Optional** — replaces `yourdomain.com` placeholder; defaults to `https://www.yourdomain.com`. Feeds `NUXT_PUBLIC_SITE_URL` + cms `BASE_URL` (canonical/hreflang) |
| `languages` | | Array like `["en","fr","de"]`. Defaults to `["en","fr","de"]` |
| `defaultLocale` | | Must be in `languages`. Defaults to `en` |
| `address`, `phone`, `email`, `workingHours` | | Footer / contact info |
| `copyright`, `year` | | Footer line |
| `logoPath` | | Path of your logo (default `/images/logo/logo.png`) |
| `externalLinks`, `socialLinks` | | Footer links |
| `nav` | | `{ "items": [ { "to": "/services", "labelKey": "nav.services" }, … ] }` → written to `site.config.json` (defaults to home/products/services/partners/blogs/about/contact) |
| `footer` | | `{ "quickLinks": […], "legalLinks": […] }` → written to `site.config.json` (defaults: quick links + privacy/terms/disclaimer) |
| `aboutPage` | | Statistics / core values / team / reasons (matches `companyInfo.aboutPage`) |
| `copy` | | Per-language i18n overrides: `{ "en": {...}, "fr": {...} }` deep-merged into that locale file. Any string under `YourBrand` / `Your Company` / `yourdomain.com` is replaced automatically across all locales |

### content JSON — what the validator checks

`meta.id`, `meta.status` (`draft`/`published`/`archived`), `overview.title`,
`overview.excerpt`; partners additionally need `meta.type`
(`company`/`institution`/`partner`/`consultant`/`training-center`); products
optionally use `meta.category` (defaults to `general`) to organise their
sub-folder under `data/products/{category}/{lang}/`.

For the **complete** schema (pricing, process, faq, highlights, geo, team,
institution…) see `server/schemas/content.ts`. The server re-validates content
at runtime and falls back to raw data if anything is off — so a slightly
incomplete file degrades gracefully instead of breaking the site.

### Asset URLs

If a JSON `cover.url` is a bare filename (e.g. `"cover.png"`) that exists under
`input/assets/{type}/{id}/`, the script copies the image and rewrites the URL to
`/api/assets/{type}/{id}/cover.png`. **Products use a category sub-folder**:
`input/assets/products/{category}/{id}/cover.webp` →
`/api/assets/products/{category}/{id}/cover.webp`. Absolute URLs and
`/api/assets/...` URLs are left untouched.

### What the script does

| # | Step | Writes to |
|---|------|-----------|
| 1 | Validate `company.json` and every content JSON (fails fast with readable errors) | – |
| 2 | Generate `utils/config.ts` from the manifest | `utils/config.ts` |
| 2b | Generate `site.config.json` (nav/footer) + `.github/workflows/deploy.yml` + `setup.ps1` + `.env` + `cms/.env` | `site.config.json`, `.github/workflows/deploy.yml`, `setup.ps1`, `.env`, `cms/.env` |
| 3 | Inject brand + per-language `copy` overrides into the locale files | `i18n/locales/{en,fr,de}.json` |
| 4 | Copy validated content, set `_type` + `meta.language` | `data/services/{lang}/`, `data/partners/{lang}/`, `data/blogs/{lang}/`, `data/products/{category}/{lang}/` |
| 5 | Copy images and rewrite `cover.url` → `/api/assets/{type}/{id}/{file}` | `data/assets/`, `public/images/logo/` |
| 6 | Sync `i18n.locales` to your manifest languages | `nuxt.config.ts` |
| 7 | `npm install` (if needed) → `npx prisma generate` → `npm run build` | `.output/` |

Everything under `data/` is gitignored (per-deployment content), so the template
repo itself stays clean.

### Limitations

- **Images are not converted** — place WebP/PNG/JPG in `input/assets/` as-is.
- **No translation/LLM** (the generator itself): each language needs its own
  content folder and, optionally, its own `copy` block. Missing locale files
  fall back to `en.json`.
- Content and images both live under `data/` and resolve from there by default.
  If you deploy content separately, set `NUXT_DATA_DIR` to that folder and both
  content and images resolve from it (see `server/utils/localizedData.ts`).
