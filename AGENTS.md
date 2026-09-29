# MCA-CMS — Multi-Language Professional Services Website Template

Nuxt 3 + i18n professional services site template (industry-neutral, de-medicalized). SSR-only (no prerender). Data-driven from filesystem JSON. Brand / nav / company info are configurable per deployment. Languages: en / fr / de.

## Source & Lineage

- This repo was **forked from the production site `C:\pyproj\medchinago`** (a live Nuxt 3 medical tourism site) and **de-branded** — all `YourBrand`/`yourdomain` references replaced with `YourBrand` / `yourdomain.com` placeholders.
- The two repos evolve **independently**. Do NOT assume a feature in one exists in the other. Do NOT push medchinago changes into this template (or vice versa) without review.
- The nav-data-driven refactor (`site.config.json` + `TheHeader`/`TheFooter`) exists **only here**. The production site still uses hardcoded nav — don't treat them as interchangeable.
- During de-branding, several hardcoded values were made dynamic; if you find more brand remnants, follow the same pattern:
  - WhatsApp link in `TheFooter.vue` derives from `companyInfo.phone`
  - share/detail URLs derive from `config.public.siteUrl || companyInfo.siteUrl`
  - `server/routes/llms.txt.ts` and `public/robots.txt` read from config / use placeholders

## Quick Start
```powershell
npm install                 # postinstall → nuxt prepare
npx prisma generate         # must run before build
$env:DATABASE_URL="file:./prisma/dev.db"; npx prisma db push
npm run dev                 # dev server at :3000
npm run build               # produces .output/
```

## Customization

See `CUSTOMIZE.md` (project root) — the single most important file for site owners.

**Site Generator** (WordPress-style quick start): `python tools/sitegen/generate.py`
reads `input/company.json` + `input/content/` + `input/assets/`, writes
`utils/config.ts`, injects brand copy into `i18n/locales/*.json`, copies content
into `data/` and runs the build. See `QUICKSTART.md` (the single manual for
both the sitegen flow and its input reference).

**Content Generator (CMS)**: `cms/` is an LLM-driven content generator
(uses the **user's own LLM API**) for the four entities — products / services /
partners / blogs. AI that is asked to operate it should read **`cms/AGENTS.md`**
(CLI + customisation guide); humans read `cms/README.md`. The generator writes
content into `data/`, same as sitegen.

| Config | Location | What it controls |
|--------|----------|------------------|
| `site.config.json` | header nav + footer quick/legal links (data-driven) |
| `utils/config.ts` | `companyInfo` — brand name, address, phone, email, siteUrl, social links, about-page data |
| `app.vue` | design tokens (`--mc-jade`, `--mc-amber`, etc.) |
| `i18n/locales/{lang}.json` | all UI strings + SEO titles per language |

## Architecture

| Directory | Purpose |
|-----------|---------|
| `server/api/blogs/` | Filesystem-backed REST endpoints (slug-first lookup) |
| `server/api/services/` | Same pattern — `data/services/` |
| `server/api/providers/` | Same pattern — `data/partners/` |
| `server/api/products/` | Same pattern — `data/products/{category}/{lang}/` |
| `server/middleware/auth.ts` | Bearer token guard for `manage`/`upload` paths |
| `data/` | Content JSON + asset images (skeleton tracked, content gitignored) |
| `prisma/schema.prisma` | SQLite, single `Contact` model |
| `ecosystem.config.cjs` | PM2 production config (adjust name/cwd per deployment) |

## Key Details

- **All dynamic pages use SSR** (`routeRules` in `nuxt.config.ts`). No prerender — content lives in `data/` at runtime.
- **Content lookup is slug-first** (`server/utils/contentApi.ts`): URL param matches `meta.slug` in JSON files. Falls back to filename-as-ID for backward compat.
- **Image URLs** use `/api/assets/{type}/{id}/{filename}.webp?v={updatedAt}` for cache busting.
- **i18n**: `@nuxtjs/i18n` v10, `prefix_except_default` (default locale has no prefix). Locales in `i18n/locales/{lang}.json`. **Never** use `v-model` on `locale` — use `:value` + `@change` + `switchLocalePath()`.
- **Custom design tokens** in `app.vue` CSS vars (`--mc-jade`, `--mc-amber`, etc.) — no Tailwind config overrides.
- **Related content (sidebars)**: computed **dynamically at runtime** by `server/api/blogs/[id]/recommendations.get.ts` (and `server/api/related.get.ts`) using **Jaccard text similarity**. Do NOT populate the static `relatedProviders`/`relatedServices` JSON fields.
- **Homepage hero is responsive**: `public/images/hero-bg.webp` (1920×1280, 4:3) ships as three WebP sizes (`hero-bg-640/1280/1920.webp`) consumed via `srcset` + `sizes="100vw"` + `fetchpriority="high"` in `pages/index.vue`; the original `hero-bg.webp` is kept for social `og:image`. Replace all four files when swapping the hero (see `CUSTOMIZE.md` §5).

## Content

Content JSON files are per-deployment and live in `data/` (gitignored; only the empty skeleton is tracked). Structure:

```
data/blogs/{lang}/*.json                         blog articles (所有站点)
data/services/{lang}/*.json                      services (服务站)
data/partners/{lang}/*.json                      partners (中介/合作站)
data/products/{category}/{lang}/*.json           products (商品站)
data/assets/{type}/{id}/*.webp                   uploaded images
```

Entity types live **side-by-side** at the top level of `data/`. A site only
needs the folders for the types it uses (e.g. a services site may skip
`products/`). Products are additionally organised by `meta.category`:
`data/products/{category}/{lang}/{slug}.json`. The blog entity's data dir and
URL route are both the plural **`blogs`** (e.g. `/blogs/{slug}`).

The companion CMS (Python CLI, in a separate repo) generates these JSONs from markdown or LLM prompts, and can sync to a remote API.

## Deployment

Suggested: GitHub Actions — push to `main` → `npm ci` → `npx prisma generate` → `npm run build` → SCP `.output/` + `ecosystem.config.cjs` to server → PM2 restart. `ecosystem.config.cjs` ships with port 3001 — adjust `cwd` and app `name` for your server.

## Important Constraints

- No lint / typecheck / test scripts configured — `npm run build` is the only verification.
- Disable `appManifest` in nuxt config (`experimental.appManifest: false`).
- Contact form writes to SQLite via Prisma. `NUXT_ADMIN_API_KEY` env for auth.
- Brand text: replace all `YourBrand` / `yourdomain.com` placeholders in `utils/config.ts`, `i18n/locales/*.json`, and `public/images/logo/`.

## SEO Title 规范

核心约束：
- **禁止**在 locale value 中使用 `|` 管道符（vue-i18n 会截断），一律用 ` - ` 替代
- 所有 page title 写死在 `i18n/locales/{lang}.json`，代码不做字符串拼接
- 全站统一使用 `useSeoMeta`（不用 `useHead` + `meta` 数组）
- Detail 页通过 `useEntitySeo` composable 的 `applySeo(seoMeta)` 统一设置
