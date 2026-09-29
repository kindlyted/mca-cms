<template>
  <Html :lang="currentLang">
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </Html>
</template>

<script setup lang="ts">
const { locale } = useI18n()

const langMap: Record<string, string> = {
  en: 'en-US',
  es: 'es-ES',
  fr: 'fr-FR',
  ja: 'ja-JP',
  ko: 'ko-KR',
  ru: 'ru-RU'
}

const currentLang = computed(() => langMap[locale.value] || 'en-US')
</script>

<style>
:root {
  /* Brand — Jade & Ink */
  --mc-jade: oklch(52% 0.16 185);
  --mc-jade-light: oklch(60% 0.14 185);
  --mc-jade-lighter: oklch(72% 0.10 185);
  --mc-jade-dark: oklch(42% 0.15 185);
  --mc-jade-darker: oklch(32% 0.12 185);
  --mc-jade-pale: oklch(92% 0.03 185);
  --mc-jade-faint: oklch(97% 0.015 185);

  --mc-amber: oklch(72% 0.14 78);
  --mc-amber-light: oklch(80% 0.10 78);
  --mc-amber-dark: oklch(60% 0.12 78);
  --mc-amber-pale: oklch(95% 0.04 78);

  /* Ink — text scale */
  --mc-ink: oklch(15% 0.008 185);
  --mc-ink-soft: oklch(32% 0.006 185);
  --mc-ink-muted: oklch(52% 0.004 185);
  --mc-ink-faint: oklch(65% 0.003 185);

  /* Surfaces */
  --mc-surface: oklch(99% 0.002 185);
  --mc-surface-alt: oklch(96.5% 0.004 185);
  --mc-surface-raised: oklch(100% 0 0);

  /* Deep sections */
  --mc-deep: oklch(18% 0.015 185);
  --mc-deep-alt: oklch(14% 0.012 185);
  --mc-deep-warm: oklch(18% 0.012 100);

  /* Semantic */
  --mc-success: oklch(62% 0.18 145);
  --mc-error: oklch(55% 0.20 25);
  --mc-info: oklch(60% 0.12 230);

  /* Borders */
  --mc-border: oklch(88% 0.004 185);
  --mc-border-strong: oklch(78% 0.006 185);
  --mc-border-jade: oklch(52% 0.16 185 / 0.2);

  /* Shadows */
  --mc-shadow-sm: 0 1px 3px oklch(0% 0 0 / 0.06), 0 1px 2px oklch(0% 0 0 / 0.04);
  --mc-shadow-md: 0 4px 12px oklch(0% 0 0 / 0.08);
  --mc-shadow-lg: 0 8px 32px oklch(0% 0 0 / 0.10);
  --mc-shadow-xl: 0 20px 60px oklch(0% 0 0 / 0.12);

  /* Motion */
  --mc-ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --mc-ease-out-quad: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --mc-ease-inout: cubic-bezier(0.76, 0, 0.24, 1);
  --mc-duration-fast: 200ms;
  --mc-duration: 400ms;
  --mc-duration-slow: 700ms;
  --mc-duration-reveal: 900ms;

  /* Z-index scale */
  --mc-z-dropdown: 100;
  --mc-z-sticky: 200;
  --mc-z-nav: 300;
  --mc-z-modal-backdrop: 400;
  --mc-z-modal: 500;
  --mc-z-toast: 600;
  --mc-z-tooltip: 700;
}

html {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  scroll-behavior: smooth;
}

body {
  margin: 0;
  padding: 0;
  background-color: var(--mc-surface);
  color: var(--mc-ink-soft);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* =====================
   Scroll Reveal System
   ===================== */

.reveal {
  opacity: 0;
  transition: opacity var(--mc-duration-reveal) var(--mc-ease-out),
              transform var(--mc-duration-reveal) var(--mc-ease-out),
              filter var(--mc-duration-reveal) var(--mc-ease-out);
}

.reveal.visible {
  opacity: 1;
  transform: none;
  filter: none;
}

.reveal-up {
  transform: translateY(32px);
}

.reveal-up.visible {
  transform: translateY(0);
}

.reveal-down {
  transform: translateY(-24px);
}

.reveal-down.visible {
  transform: translateY(0);
}

.reveal-left {
  transform: translateX(-32px);
}

.reveal-left.visible {
  transform: translateX(0);
}

.reveal-right {
  transform: translateX(32px);
}

.reveal-right.visible {
  transform: translateX(0);
}

.reveal-scale {
  transform: scale(0.95);
}

.reveal-scale.visible {
  transform: scale(1);
}

.reveal-blur {
  filter: blur(8px);
}

.reveal-blur.visible {
  filter: blur(0);
}

/* Stagger children */
.reveal-stagger > .reveal-child {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.7s var(--mc-ease-out),
              transform 0.7s var(--mc-ease-out);
}

.reveal-stagger.visible > .reveal-child {
  opacity: 1;
  transform: translateY(0);
}

/* Image zoom container */
.img-zoom {
  overflow: hidden;
}

.img-zoom img {
  transition: transform 0.6s var(--mc-ease-out);
}

.img-zoom:hover img {
  transform: scale(1.08);
}

/* Card hover lift */
.card-hover {
  transition: transform var(--mc-duration) var(--mc-ease-out),
              box-shadow var(--mc-duration) var(--mc-ease-out),
              border-color var(--mc-duration) var(--mc-ease-out);
}

.card-hover:hover {
  transform: translateY(-4px);
  box-shadow: var(--mc-shadow-lg);
}

/* Button base */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 600;
  border-radius: 8px;
  transition: all var(--mc-duration) var(--mc-ease-out);
  cursor: pointer;
  border: none;
  text-decoration: none;
}

.btn-primary {
  background: var(--mc-jade);
  color: white;
  box-shadow: 0 4px 14px oklch(52% 0.16 185 / 0.3);
}

.btn-primary:hover {
  background: var(--mc-jade-dark);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px oklch(52% 0.16 185 / 0.35);
}

.btn-amber {
  background: var(--mc-amber);
  color: var(--mc-ink);
  box-shadow: 0 4px 14px oklch(72% 0.14 78 / 0.3);
}

.btn-amber:hover {
  background: var(--mc-amber-dark);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px oklch(72% 0.14 78 / 0.35);
}

.btn-outline {
  background: transparent;
  border: 2px solid var(--mc-border-strong);
  color: var(--mc-ink-soft);
}

.btn-outline:hover {
  border-color: var(--mc-jade);
  color: var(--mc-jade);
  transform: translateY(-2px);
}

.btn-outline-light {
  background: transparent;
  border: 2px solid oklch(100% 0 0 / 0.3);
  color: white;
}

.btn-outline-light:hover {
  border-color: white;
  background: oklch(100% 0 0 / 0.1);
  transform: translateY(-2px);
}

/* Section spacing */
.section {
  padding: 5rem 0;
}

@media (min-width: 768px) {
  .section {
    padding: 6rem 0;
  }
}

@media (min-width: 1024px) {
  .section {
    padding: 7rem 0;
  }
}

.section-head {
  text-align: center;
  margin-bottom: 3.5rem;
}

.section-head h2 {
  font-size: clamp(1.75rem, 3.5vw, 2.5rem);
  font-weight: 700;
  line-height: 1.2;
  color: var(--mc-ink);
  margin-bottom: 0.75rem;
}

.section-head p {
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--mc-ink-muted);
  max-width: 600px;
  margin: 0 auto;
}

/* =====================
   Shared component styles
   ===================== */

.spinner-jade {
  border-color: var(--mc-jade);
  border-top-color: transparent;
}

/* Breadcrumb jade theme */
.breadcrumb-jade .ubreadcrumb-base {
  color: var(--mc-ink-muted);
  transition: color var(--mc-duration-fast) var(--mc-ease-out);
}
.breadcrumb-jade .ubreadcrumb-base:hover {
  color: var(--mc-jade);
}
.breadcrumb-jade .ubreadcrumb-active {
  color: var(--mc-ink-soft);
}
.breadcrumb-jade .ubreadcrumb-label {
  color: var(--mc-ink-muted);
}
.breadcrumb-jade .ubreadcrumb-divider {
  color: var(--mc-ink-faint);
}

/* Jade solid button (inline use) */
.btn-jade-solid {
  background: var(--mc-jade);
  transition: background var(--mc-duration-fast) var(--mc-ease-out), transform var(--mc-duration-fast) var(--mc-ease-out);
}
.btn-jade-solid:hover {
  background: var(--mc-jade-dark);
  transform: translateY(-1px);
}

/* Form controls */
.input-jade {
  border-color: var(--mc-border);
  color: var(--mc-ink-soft);
  transition: border-color var(--mc-duration-fast) var(--mc-ease-out), box-shadow var(--mc-duration-fast) var(--mc-ease-out);
}
.input-jade:focus {
  outline: none;
  border-color: var(--mc-jade-lighter);
  box-shadow: 0 0 0 3px oklch(52% 0.16 185 / 0.15);
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .reveal,
  .reveal-up,
  .reveal-down,
  .reveal-left,
  .reveal-right,
  .reveal-scale,
  .reveal-blur,
  .reveal-stagger > .reveal-child {
    opacity: 1 !important;
    transform: none !important;
    filter: none !important;
    transition: none !important;
  }

  html {
    scroll-behavior: auto;
  }

  .card-hover:hover {
    transform: none;
  }

  .btn-primary:hover,
  .btn-amber:hover,
  .btn-outline:hover,
  .btn-outline-light:hover {
    transform: none;
  }

  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
