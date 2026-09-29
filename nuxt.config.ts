import { resolve } from 'node:path'
import { companyInfo } from './utils/config'

export default defineNuxtConfig({
  compatibilityDate: '2026-03-04',
  devtools: { enabled: true },
  modules: [
    '@nuxt/ui',
    '@nuxt/icon',
    '@nuxtjs/i18n'
  ],
  
  i18n: {
    baseUrl: process.env.NUXT_PUBLIC_SITE_URL || companyInfo.siteUrl,
    locales: [
      { 
        code: 'en', 
        iso: 'en-US', 
        file: 'en.json',  // 相对于 i18n 目录
        name: 'English' 
      },
      { 
        code: 'fr', 
        iso: 'fr-FR', 
        file: 'fr.json', 
        name: 'Français' 
      },
      { 
        code: 'de', 
        iso: 'de-DE', 
        file: 'de.json', 
        name: 'Deutsch' 
      }
    ],
    defaultLocale: 'en',
    strategy: 'prefix_except_default',
    // lazy: true,  // ❌ v10 已移除，删除这行
    // langDir: 'locales',  // ❌ v10 已移除，删除这行
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root'
    },
    vueI18n: './i18n.config.ts'  // ✅ 保持这个配置
  },

  // App configuration
  app: {
    head: {
      title: `${companyInfo.shortName} - Professional Services & Solutions`,
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { 
          name: 'description', 
          content: companyInfo.description
        },
        { 
          name: 'keywords', 
          content: 'professional services, business solutions, consulting, company website' 
        }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  // Runtime configuration
  runtimeConfig: {
    // Data directory configuration (can be overridden via NUXT_DATA_DIR env var)
    dataDir: process.env.NUXT_DATA_DIR || undefined,

    // Admin API Key (for sensitive operations like article publishing)
    adminApiKey: process.env.NUXT_ADMIN_API_KEY || '',


    public: {
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || companyInfo.siteUrl,
      gaId: process.env.NUXT_PUBLIC_GA_ID || ''
    }
  },

  // Nitro configuration
  nitro: {
    prerender: {
      routes: []
      // Note: /news removed; /, /services, /partners, /blog no longer prerendered
      // data/ is gitignored, so prerender would produce empty pages on CI/CD build
      // All pages now use SSR to ensure fresh data from production data directory
    },
    // Route rules
    routeRules: {
      // Homepage - Link header for agent discovery (RFC 8288)
      '/': {
        headers: { 'Link': '</llms.txt>; rel="service-doc", </sitemap.xml>; rel="sitemap"' }
      },
      // Sitemap XML - 强制正确的 Content-Type
      '/sitemap.xml': {
        headers: { 'Content-Type': 'application/xml; charset=utf-8' }
      },
      // Service pages - 依赖服务端 API 数据，不预渲染
      '/services': {
        ssr: true,
        prerender: false
      },
      '/services/**': {
        ssr: true,
        prerender: false
      },
      // Partner pages - 依赖服务端 API 数据，不预渲染
      '/partners': {
        ssr: true,
        prerender: false
      },
      '/partners/**': {
        ssr: true,
        prerender: false
      },
      // Admin pages - prevent search engine indexing
      '/admin/**': {
        ssr: false,
        headers: { 'X-Robots-Tag': 'noindex, nofollow' }
      },
      // Product pages - 依赖服务端 API 数据，不预渲染
      '/products': {
        ssr: true,
        prerender: false
      },
      '/products/**': {
        ssr: true,
        prerender: false
      },
      // Blog pages use SSR, no prerendering
      '/blogs': {
        ssr: true,
        prerender: false
      },
      // Blog detail pages use SSR, no prerendering
      '/blogs/**': {
        ssr: true,
        prerender: false
      }
    }
  },

  // Experimental features
  experimental: {
    // Disable app manifest to avoid Vite resolving `#app-manifest` in dev
    appManifest: false,
    // Inline critical CSS for first paint — reduces render-blocking CSS
    inlineSSRStyles: true
  },

  // Development server configuration
  devServer: {
    port: 3000
  }
})