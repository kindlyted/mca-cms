import { readdirSync, statSync, readFileSync, existsSync } from 'fs'
import { join, resolve } from 'path'

interface SitemapUrl {
  loc: string
  priority: number
  changefreq: string
  lastmod: string
}

// 简单的内存缓存
let cachedSitemap: string | null = null
let cacheTime = 0
const CACHE_DURATION = 60 * 60 * 1000 // 1小时缓存

// 获取文件最后修改日期
function getFileLastMod(filePath: string): string {
  try {
    const stats = statSync(filePath)
    return stats.mtime.toISOString()
  } catch {
    return new Date().toISOString()
  }
}

// 从 JSON 文件中读取日期字段
function getJsonDate(filePath: string): string | undefined {
  try {
    const content = readFileSync(filePath, 'utf-8')
    const data = JSON.parse(content)
    const dateStr = data.meta?.updatedAt || data.meta?.createdAt || data.content?.updatedAt || data.content?.publishedAt || data.updatedAt || data.publishedAt
    if (dateStr) {
      return new Date(dateStr).toISOString()
    }
  } catch {
    // 解析失败
  }
  return undefined
}

// 递归扫描目录下所有 .json 文件
function scanJsonFiles(dir: string): string[] {
  const results: string[] = []
  try {
    const entries = readdirSync(dir, { withFileTypes: true })
    for (const entry of entries) {
      const fullPath = join(dir, entry.name)
      if (entry.isDirectory()) {
        results.push(...scanJsonFiles(fullPath))
      } else if (entry.name.endsWith('.json')) {
        results.push(fullPath)
      }
    }
  } catch {
    // 目录不存在
  }
  return results
}

// 从文件路径提取 locale
function parseLocale(filePath: string, baseDir: string): string | null {
  const relative = filePath.slice(baseDir.length + 1).replace(/\\/g, '/')
  const parts = relative.split('/')
  return parts.length >= 2 ? parts[0] : null
}

// 从 JSON 文件中读取 meta.slug，没有则回退到文件名（去掉 .json）
function getEntitySlug(filePath: string): string {
  try {
    const content = readFileSync(filePath, 'utf-8')
    const data = JSON.parse(content)
    if (data.meta?.slug) {
      return data.meta.slug
    }
  } catch {}
  // 回退：从文件名提取
  const name = filePath.replace(/\\/g, '/').split('/').pop() || ''
  return name.replace('.json', '')
}

export default defineEventHandler(async (event) => {
  const now = Date.now()

  // 检查缓存
  if (cachedSitemap && (now - cacheTime) < CACHE_DURATION) {
    event.node.res.setHeader('Content-Type', 'application/xml; charset=utf-8')
    event.node.res.setHeader('Cache-Control', 'public, max-age=3600')
    event.node.res.end(cachedSitemap)
    return
  }

  const config = useRuntimeConfig(event)
  const dataDir = config.dataDir || resolve(process.cwd(), 'data')
  const baseUrl = config.public.siteUrl || companyInfo.siteUrl
  const isoNow = new Date().toISOString()

  // 语言前缀映射（i18n strategy: prefix_except_default）
  const localePrefix: Record<string, string> = {
    en: '',
    fr: '/fr',
    de: '/de'
  }

  const urls: SitemapUrl[] = []

  // 为每个语言生成基础路由
  const baseRoutes = [
    { path: '', priority: '1', changefreq: 'weekly' },           // 首页
    { path: '/products', priority: '0.8', changefreq: 'weekly' },
    { path: '/services', priority: '0.8', changefreq: 'weekly' },
    { path: '/partners', priority: '0.8', changefreq: 'weekly' },
    { path: '/blogs', priority: '0.8', changefreq: 'weekly' },
    { path: '/about', priority: '0.7', changefreq: 'monthly' },
    { path: '/contact', priority: '0.7', changefreq: 'monthly' },
    { path: '/privacy', priority: '0.5', changefreq: 'yearly' },
    { path: '/terms', priority: '0.5', changefreq: 'yearly' },
    { path: '/disclaimer', priority: '0.5', changefreq: 'yearly' }
  ]

  for (const [locale, prefix] of Object.entries(localePrefix)) {
    for (const route of baseRoutes) {
      urls.push({
        loc: `${baseUrl}${prefix}${route.path}`,
        priority: route.priority,
        changefreq: route.changefreq,
        lastmod: isoNow
      })
    }
  }

  try {
    // 扫描商品页面: data/products/{category}/<locale>/*.json
    const productsBase = join(dataDir, 'products')
    if (existsSync(productsBase)) {
      const categories = readdirSync(productsBase, { withFileTypes: true }).filter(e => e.isDirectory())
      for (const cat of categories) {
        const catDir = join(productsBase, cat.name)
        const productFiles = scanJsonFiles(catDir)
        for (const filePath of productFiles) {
          const locale = parseLocale(filePath, catDir)
          if (!locale || !(locale in localePrefix)) continue
          const prefix = localePrefix[locale]

          const slug = getEntitySlug(filePath)
          const lastmod = getJsonDate(filePath) || getFileLastMod(filePath)
          urls.push({
            loc: `${baseUrl}${prefix}/products/${slug}`,
            priority: '0.8',
            changefreq: 'monthly',
            lastmod
          })
        }
      }
    }

    // 扫描服务页面: data/services/<locale>/*.json
    const servicesDir = join(dataDir, 'services')
    const serviceFiles = scanJsonFiles(servicesDir)

    for (const filePath of serviceFiles) {
      const locale = parseLocale(filePath, servicesDir)
      if (!locale || !(locale in localePrefix)) continue
      const prefix = localePrefix[locale]

      const slug = getEntitySlug(filePath)
      const lastmod = getJsonDate(filePath) || getFileLastMod(filePath)
      urls.push({
        loc: `${baseUrl}${prefix}/services/${slug}`,
        priority: '0.8',
        changefreq: 'monthly',
        lastmod
      })
    }

    // 扫描 partner 详情页: data/partners/<locale>/*.json
    const partnersDir = join(dataDir, 'partners')
    const partnerFiles = scanJsonFiles(partnersDir)

    for (const filePath of partnerFiles) {
      const locale = parseLocale(filePath, partnersDir)
      if (!locale || !(locale in localePrefix)) continue
      const prefix = localePrefix[locale]

      const slug = getEntitySlug(filePath)
      const lastmod = getJsonDate(filePath) || getFileLastMod(filePath)
      urls.push({
        loc: `${baseUrl}${prefix}/partners/${slug}`,
        priority: '0.8',
        changefreq: 'monthly',
        lastmod
      })
    }

    // 扫描博客页面: data/blogs/<locale>/*.json
    const blogDir = join(dataDir, 'blogs')
    const blogFiles = scanJsonFiles(blogDir)

    for (const filePath of blogFiles) {
      const locale = parseLocale(filePath, blogDir)
      if (!locale || !(locale in localePrefix)) continue
      const prefix = localePrefix[locale]

      const slug = getEntitySlug(filePath)
      const lastmod = getJsonDate(filePath) || getFileLastMod(filePath)
      urls.push({
        loc: `${baseUrl}${prefix}/blogs/${slug}`,
        priority: '0.7',
        changefreq: 'monthly',
        lastmod
      })
    }
  } catch (error) {
    console.error('Error generating sitemap:', error)
  }

  // Debug: log URL counts per locale for troubleshooting
  const localeCounts: Record<string, number> = { en: 0, fr: 0, de: 0 }
  for (const u of urls) {
    for (const loc of Object.keys(localeCounts)) {
      const prefix = loc === 'en' ? `${baseUrl}/` : `${baseUrl}/${loc}/`
      if (u.loc.startsWith(prefix)) {
        localeCounts[loc]++
        break
      }
    }
  }
  console.log(`[sitemap] Total URLs: ${urls.length} | EN: ${localeCounts.en} | FR: ${localeCounts.fr} | ES: ${localeCounts.es}`)

  // 生成 XML — 与参考站格式一致：简单、每个 URL 独立一行
  const xmlBody = urls.map(u =>
    '<url>\n' +
    `<loc>${u.loc}</loc>\n` +
    `<lastmod>${u.lastmod}</lastmod>\n` +
    `<changefreq>${u.changefreq}</changefreq>\n` +
    `<priority>${u.priority}</priority>\n` +
    '</url>'
  ).join('\n')

  const xml = '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    xmlBody + '\n' +
    '</urlset>'

  // 更新缓存
  cachedSitemap = xml
  cacheTime = now

  event.node.res.setHeader('Content-Type', 'application/xml; charset=utf-8')
  event.node.res.setHeader('Cache-Control', 'public, max-age=3600')
  event.node.res.end(xml)
})
