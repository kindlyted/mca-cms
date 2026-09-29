import { readdirSync, readFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'

/**
 * Generic related content API
 * Given an entity type + slug, returns related services and partners
 * based on text similarity across seo.keywords, seo.description, overview.title, overview.excerpt, body
 */

function getDataRoot() {
  return join(process.cwd(), 'data')
}

interface EntitySummary {
  id: string
  slug: string
  title: string
  excerpt: string
  coverImage: string | null
  link: string
  // For scoring
  _text: string
  _keywords: string
}

function versionAssetUrl(rawImage: string | undefined, version: string | undefined): string {
  if (!rawImage) return ''
  const v = version ? `?v=${new Date(version).getTime()}` : ''
  return `${rawImage}${v}`
}

function buildEntitySummary(entity: any, fileId: string, type: 'service' | 'partner' | 'product', lang: string): EntitySummary {
  const slug = entity.meta?.slug || fileId
  const title = entity.overview?.title || ''
  const excerpt = entity.overview?.excerpt || ''
  const rawImage = entity.cover?.url || entity.visuals?.cover?.url || entity.visuals?.thumbnail?.url
  const image = versionAssetUrl(rawImage, entity.meta?.updatedAt)

  // Build searchable text: weight keywords higher by repeating them
  const keywords = (entity.seo?.keywords || '').toLowerCase()
  const description = (entity.seo?.description || '').toLowerCase()
  const bodyText = typeof entity.body === 'string' ? entity.body : (entity.body?.content || '')
  const bodyPreview = bodyText.slice(0, 800).toLowerCase()

  // Keywords get 3x weight, title gets 2x weight
  const searchText = [
    keywords, keywords, keywords,
    title.toLowerCase(), title.toLowerCase(),
    description,
    excerpt.toLowerCase(),
    bodyPreview
  ].join(' ')

  return {
    id: entity.meta?.id || fileId,
    slug,
    title,
    excerpt,
    coverImage: image || null,
    link: type === 'service' ? `/services/${slug}` : type === 'product' ? `/products/${slug}` : `/partners/${slug}`,
    _text: searchText,
    _keywords: keywords
  }
}

/**
 * Compute a relevance score between a source entity and a target entity
 * Uses keyword overlap (weighted 0.5) + text token overlap (weighted 0.5)
 */
function computeRelevance(source: EntitySummary, target: EntitySummary): number {
  // 1. Keyword-level match: split keywords by comma/space
  const sourceKws = new Set(
    source._keywords
      .split(/[,\s]+/)
      .map(k => k.trim())
      .filter(k => k.length > 2)
  )
  const targetKws = new Set(
    target._keywords
      .split(/[,\s]+/)
      .map(k => k.trim())
      .filter(k => k.length > 2)
  )

  let keywordScore = 0
  if (sourceKws.size > 0 && targetKws.size > 0) {
    const intersection = new Set([...sourceKws].filter(k => targetKws.has(k)))
    keywordScore = intersection.size / Math.max(sourceKws.size, targetKws.size)
  }

  // 2. Text-level match: tokenize and compute Jaccard
  const tokenize = (text: string): Set<string> => {
    const tokens = text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(t => t.length > 3) // skip short words
    return new Set(tokens)
  }

  const sourceTokens = tokenize(source._text)
  const targetTokens = tokenize(target._text)

  let textScore = 0
  if (sourceTokens.size > 0 && targetTokens.size > 0) {
    const intersection = new Set([...sourceTokens].filter(t => targetTokens.has(t)))
    textScore = intersection.size / Math.max(sourceTokens.size, targetTokens.size)
  }

  return keywordScore * 0.5 + textScore * 0.5
}

function loadEntities(dir: string): { fileId: string; data: any }[] {
  if (!existsSync(dir)) return []
  const files = readdirSync(dir).filter(f => f.endsWith('.json'))
  return files.map(file => {
    const content = readFileSync(join(dir, file), 'utf-8')
    return { fileId: file.replace('.json', ''), data: JSON.parse(content) }
  })
}

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const entityType = query.entityType as string
  const slug = query.slug as string
  const lang = (query.lang as string) || 'en'

  if (!entityType || !slug) {
    throw createError({ statusCode: 400, statusMessage: 'entityType and slug are required' })
  }

  const dataRoot = getDataRoot()

  // Load all services and partners
  const servicesDir = join(dataRoot, 'services', lang)
  const partnersDir = join(dataRoot, 'partners', lang)

  const serviceFiles = loadEntities(servicesDir)
  const partnerFiles = loadEntities(partnersDir)

  // Products live in per-category subdirs: data/products/{category}/{lang}
  const productFiles: { fileId: string; data: any }[] = []
  const productsBase = join(dataRoot, 'products')
  if (existsSync(productsBase)) {
    const categories = readdirSync(productsBase, { withFileTypes: true }).filter(e => e.isDirectory())
    for (const cat of categories) {
      productFiles.push(...loadEntities(join(productsBase, cat.name, lang)))
    }
  }

  // Build summaries
  const serviceSummaries = serviceFiles.map(f =>
    buildEntitySummary(f.data, f.fileId, 'service', lang)
  )
  const partnerSummaries = partnerFiles.map(f =>
    buildEntitySummary(f.data, f.fileId, 'partner', lang)
  )
  const productSummaries = productFiles.map(f =>
    buildEntitySummary(f.data, f.fileId, 'product', lang)
  )

  const result: { relatedServices: any[], relatedPartners: any[], relatedProducts: any[] } = {
    relatedServices: [],
    relatedPartners: [],
    relatedProducts: []
  }

  // Find the source entity
  let sourceSummary: EntitySummary | null = null

  if (entityType === 'service') {
    sourceSummary = serviceSummaries.find(s => s.slug === slug || s.id === slug) || null
  } else if (entityType === 'partner') {
    sourceSummary = partnerSummaries.find(p => p.slug === slug || p.id === slug) || null
  } else if (entityType === 'product') {
    sourceSummary = productSummaries.find(p => p.slug === slug || p.id === slug) || null
  }

  if (!sourceSummary) {
    // If source not found (e.g. blog), try to load blog data
    if (entityType === 'blog') {
      const blogDir = join(dataRoot, 'blogs', lang)
      const blogFiles = loadEntities(blogDir)
      const blogEntity = blogFiles.find(f =>
        f.data.meta?.slug === slug || f.fileId === slug
      )
      if (blogEntity) {
        // Build a pseudo summary from blog
        const blogTitle = blogEntity.data.overview?.title || ''
        const blogExcerpt = blogEntity.data.overview?.excerpt || ''
        const blogKeywords = blogEntity.data.seo?.keywords || ''
        const blogBody = typeof blogEntity.data.body === 'string'
          ? blogEntity.data.body
          : (blogEntity.data.body?.content || '')

        // Also include blog tags for better matching
        const tagNames = [
          ...(blogEntity.data.tags?.primary || []).map((t: any) => t.name || t.id || ''),
          ...(blogEntity.data.tags?.secondary || []).map((t: any) => t.name || t.id || '')
        ].filter(Boolean).join(' ')

        const searchText = [
          blogKeywords, blogKeywords, blogKeywords,
          blogTitle.toLowerCase(), blogTitle.toLowerCase(),
          blogExcerpt.toLowerCase(),
          blogBody.slice(0, 800).toLowerCase(),
          tagNames.toLowerCase(), tagNames.toLowerCase()
        ].join(' ')

        sourceSummary = {
          id: slug,
          slug,
          title: blogTitle,
          excerpt: blogExcerpt,
          coverImage: null,
          link: `/blogs/${slug}`,
          _text: searchText,
          _keywords: blogKeywords
        }
      }
    }
  }

  if (!sourceSummary) {
    return { success: true, ...result }
  }

  // Compute relevance for services (exclude self if service page)
  if (entityType !== 'service') {
    result.relatedServices = serviceSummaries
      .map(s => ({
        ...s,
        score: computeRelevance(sourceSummary!, s)
      }))
      .filter(s => s.score > 0.01)
      .sort((a, b) => b.score - a.score)
      .slice(0, 3)
      .map(({ _text, _keywords, ...rest }) => rest)
  }

  // Compute relevance for partners (exclude self if partner page)
  if (entityType !== 'partner') {
    result.relatedPartners = partnerSummaries
      .map(p => ({
        ...p,
        score: computeRelevance(sourceSummary!, p)
      }))
      .filter(p => p.score > 0.01)
      .sort((a, b) => b.score - a.score)
      .slice(0, 3)
      .map(({ _text, _keywords, ...rest }) => rest)
  }

  // Compute relevance for products (exclude self if product page)
  if (entityType !== 'product') {
    result.relatedProducts = productSummaries
      .map(p => ({
        ...p,
        score: computeRelevance(sourceSummary!, p)
      }))
      .filter(p => p.score > 0.01)
      .sort((a, b) => b.score - a.score)
      .slice(0, 6)
      .map(({ _text, _keywords, ...rest }) => rest)
  }

  return { success: true, ...result }
})
