import { readdirSync, readFileSync, existsSync } from 'fs'
import { join, resolve } from 'path'
import { companyInfo } from '../../utils/config'

let cachedContent: string | null = null
let cacheTime = 0
const CACHE_DURATION = 60 * 60 * 1000 // 1 hour

function scanEntityTitles(dir: string): { title: string; slug: string }[] {
  const results: { title: string; slug: string }[] = []
  try {
    const files = readdirSync(dir).filter(f => f.endsWith('.json'))
    for (const file of files) {
      const filePath = join(dir, file)
      let slug = ''
      let title = ''
      let status = 'draft'
      try {
        const content = readFileSync(filePath, 'utf-8')
        const data = JSON.parse(content)
        slug = data.meta?.slug || file.replace('.json', '')
        title = data.overview?.title || slug
        status = data.meta?.status || 'draft'
      } catch {
        slug = file.replace('.json', '')
        title = slug
      }
      if (status !== 'published') continue
      results.push({ title, slug })
    }
  } catch {}
  results.sort((a, b) => a.title.localeCompare(b.title))
  return results
}

export default defineEventHandler(async (event) => {
  const now = Date.now()

  if (cachedContent && (now - cacheTime) < CACHE_DURATION) {
    event.node.res.setHeader('Content-Type', 'text/plain; charset=utf-8')
    event.node.res.setHeader('Cache-Control', 'public, max-age=3600')
    event.node.res.end(cachedContent)
    return
  }

  const config = useRuntimeConfig(event)
  const dataDir = config.dataDir || resolve(process.cwd(), 'data')
  const baseUrl = config.public.siteUrl || companyInfo.siteUrl

  const languages: Record<string, string> = {
    en: 'English',
    fr: 'Français',
    de: 'Deutsch'
  }

  const lines: string[] = []
  const add = (s: string) => lines.push(s)

  add(`# ${companyInfo.shortName}`)
  add('')
  add(`${companyInfo.shortName} ${companyInfo.description}`)
  add('')

  // === Core Pages ===
  add('## Core Pages')
  add('')
  const corePages = [
    { path: '', label: 'Home' },
    { path: '/products', label: 'Products' },
    { path: '/services', label: 'Services' },
    { path: '/partners', label: 'Partners' },
    { path: '/blogs', label: 'Blog' },
    { path: '/about', label: 'About Us' },
    { path: '/contact', label: 'Contact' },
  ]
  for (const page of corePages) {
    add(`- ${page.label}: ${baseUrl}${page.path}`)
  }
  add('')

  // === Products ===
  const productsBase = join(dataDir, 'products')
  if (existsSync(productsBase)) {
    const categories = readdirSync(productsBase, { withFileTypes: true }).filter(e => e.isDirectory())
    for (const cat of categories) {
      const products = scanEntityTitles(join(productsBase, cat.name, 'en'))
      if (products.length > 0) {
        add(`## Products (${cat.name})`)
        add('')
        for (const p of products) {
          add(`- ${p.title}: ${baseUrl}/products/${p.slug}`)
        }
        add('')
      }
    }
  }

  // === Services ===
  const serviceDir = join(dataDir, 'services', 'en')
  if (existsSync(serviceDir)) {
    const services = scanEntityTitles(serviceDir)
    if (services.length > 0) {
      add('## Services')
      add('')
      for (const svc of services) {
        add(`- ${svc.title}: ${baseUrl}/services/${svc.slug}`)
      }
      add('')
    }
  }

  // === Blog Articles ===
  const blogDir = join(dataDir, 'blogs', 'en')
  if (existsSync(blogDir)) {
    const blogs = scanEntityTitles(blogDir)
    // Group blogs heuristically
    const guides = blogs.filter(b =>
      /guide|how-to|how to|insights|faq|comparison/i.test(b.title)
    )
    const news = blogs.filter(b =>
      /news|update|report|announcement|research/i.test(b.title)
    )
    const otherBlogs = blogs.filter(b =>
      !guides.includes(b) && !news.includes(b)
    )

    if (guides.length > 0) {
      add('## Guides & Insights')
      add('')
      for (const b of guides) {
        add(`- ${b.title}: ${baseUrl}/blogs/${b.slug}`)
      }
      add('')
    }

    if (news.length > 0) {
      add('## News & Updates')
      add('')
      for (const b of news) {
        add(`- ${b.title}: ${baseUrl}/blogs/${b.slug}`)
      }
      add('')
    }

    if (otherBlogs.length > 0) {
      add('## Articles')
      add('')
      for (const b of otherBlogs) {
        add(`- ${b.title}: ${baseUrl}/blogs/${b.slug}`)
      }
      add('')
    }
  }

  // === Partners ===
  const partnerDir = join(dataDir, 'partners', 'en')
  if (existsSync(partnerDir)) {
    const partners = scanEntityTitles(partnerDir)
    if (partners.length > 0) {
      add('## Partners')
      add('')
      for (const p of partners) {
        add(`- ${p.title}: ${baseUrl}/partners/${p.slug}`)
      }
      add('')
    }
  }

  // === About ===
  add(`## About ${companyInfo.shortName}`)
  add('')
  add(`${companyInfo.name} — ${companyInfo.description}`)
  add('')
  add(`Phone: ${companyInfo.phone}`)
  add(`Email: ${companyInfo.email}`)
  add(`Address: ${companyInfo.address}`)
  add('')

  // === Languages ===
  add('## Languages')
  add('')
  for (const [code, name] of Object.entries(languages)) {
    const prefix = code === 'en' ? '' : `/${code}`
    add(`- ${name}: ${baseUrl}${prefix}`)
  }

  const output = lines.join('\n')

  // Cache & respond
  cachedContent = output
  cacheTime = now

  console.log(`[llms.txt] Generated with ${lines.length} lines`)

  event.node.res.setHeader('Content-Type', 'text/plain; charset=utf-8')
  event.node.res.setHeader('Cache-Control', 'public, max-age=3600')
  event.node.res.end(output)
})
