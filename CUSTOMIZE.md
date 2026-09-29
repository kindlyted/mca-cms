# Site Customization Guide

This template is designed so that site owners can customize navigation and branding **without touching application code**. Everything you need to change lives in a small set of config files, documented below.

## 1. Navigation (header + footer)

### Header menu — `site.config.json` → `nav.items`

Edit the `nav.items` array. Each item supports:

| Field | Required | Meaning |
|-------|----------|---------|
| `to` | yes | Route path (e.g. `/services`). Do **not** prefix the locale — the app adds it automatically. |
| `labelKey` | yes | i18n key for the label (text lives in `i18n/locales/{lang}.json`). |
| `enabled` | no | Set `false` to hide the item without deleting it. |

```json
{
  "nav": {
    "items": [
      { "to": "/", "labelKey": "nav.home" },
      { "to": "/services", "labelKey": "nav.services" },
      { "to": "/blogs", "labelKey": "nav.stories" },
      { "to": "/contact", "labelKey": "nav.contact", "enabled": false }
    ]
  }
}
```

- **Add** a link → append an object with an existing `labelKey` (or add a new key to all `i18n/locales/*.json` files).
- **Reorder** → move the objects.
- **Remove** → delete the object, or keep it with `"enabled": false`.

### Footer quick links — `site.config.json` → `footer.quickLinks`

Same structure as `nav.items`. These are the links under "Quick Links".

### Footer legal links — `site.config.json` → `footer.legalLinks`

Same structure. Defaults are Privacy / Terms / Disclaimer.

### Labels / text

The actual link text is **not** in `site.config.json`. It's defined once per language in:

```
i18n/locales/en.json   →  "nav": { "home": "Home", ... },  "footer": { ... }
i18n/locales/fr.json
i18n/locales/de.json
```

Add a new label key in **all three** files (or at minimum the default `en`).

## 2. Company / brand info

File: `utils/config.ts` → `companyInfo` object.

- `name`, `shortName` — used in schema markup and titles
- `address`, `phone`, `email`, `workingHours` — shown in the footer
- `copyright` — footer copyright line
- `siteUrl` — override via `NUXT_PUBLIC_SITE_URL` env var (see `nuxt.config.ts`)
- `description` — meta / schema description
- `logoPath` — put your logo in `public/images/logo/` and point here
- `externalLinks` — footer "Resources" links
- `socialLinks` — social profile URLs
- `aboutPage` — structural data for the About page (numbers/icons are hard values; all text via `*Key` i18n references)

## 3. Design tokens / colors

`app.vue` defines CSS custom properties (`--mc-jade`, `--mc-amber`, etc.). Change these values to re-brand the whole site's color scheme — no Tailwind config edits required.

## 4. Languages

`nuxt.config.ts` `i18n.locales` + `i18n/locales/{en,fr,de}.json`. The header language dropdown renders from `availableLocales` automatically.

## 5. Homepage hero image (responsive)

The homepage LCP hero uses a **responsive image** (`public/images/hero-bg.webp`, 1920×1280, 4:3) served in three WebP sizes so mobile devices don't download the full 500 KB file.

| File | Size | Used for |
|------|------|----------|
| `hero-bg-640.webp` | 640×427 | small / mobile viewports |
| `hero-bg-1280.webp` | 1280×853 | tablet / laptop |
| `hero-bg-1920.webp` | 1920×1280 | large desktop (and `<img>` default) |
| `hero-bg.webp` | 1920×1280 | kept for `og:image` / `twitter:image` social shares |

`pages/index.vue` uses `srcset` + `sizes="100vw"` + `fetchpriority="high"`, so the browser picks the smallest sufficient size.

**When you replace the hero image**, provide all **four** files (keep 4:3 / 1920×1280). From ImageMagick:

```powershell
magick hero-bg.webp -resize 640x427  -quality 70 hero-bg-640.webp
magick hero-bg.webp -resize 1280x853 -quality 70 hero-bg-1280.webp
magick hero-bg.webp -resize 1920x1280 -quality 70 hero-bg-1920.webp
```

> `ref="heroBg"` (parallax) only drives a CSS transform and is unaffected by `srcset`. No `<link rel="preload">` is added: the hero is the first `<img>` in the HTML with `fetchpriority="high"`, so preload adds nothing.

## Important notes

- **Never** use `v-model` on the locale — the header uses `:value` + `@change` + `switchLocalePath()` (race-condition fix, see `TODO.md`).
- Image URLs use `/api/assets/{type}/{id}/{filename}.webp?v={updatedAt}` — keep the `?v=` cache-buster when swapping assets.
- `data/` is gitignored — content JSONs are per-deployment, not part of the template.
