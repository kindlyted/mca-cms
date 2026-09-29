import { readFile, readdir } from 'node:fs/promises'
import { join } from 'node:path'
import { analyzeContent, calculateTagSimilarity } from '~/utils/contentMatcher'

// 获取项目根目录
function getDataRoot() {
  return join(process.cwd(), 'data')
}

/**
 * 通过 slug 查找文章文件
 */
async function findArticleBySlug(dataDir: string, slug: string, lang: string): Promise<{ id: string; data: any } | null> {
  const blogDir = join(dataDir, 'blogs', lang)

  try {
    const files = await readdir(blogDir)
    const jsonFiles = files.filter(f => f.endsWith('.json'))

    for (const file of jsonFiles) {
      try {
        const filePath = join(blogDir, file)
        const content = await readFile(filePath, 'utf8')
        const article = JSON.parse(content)

        if (article.meta?.slug === slug) {
          return {
            id: file.replace('.json', ''),
            data: article
          }
        }
      } catch {
        continue
      }
    }
  } catch {
    // 目录不存在
  }

  return null
}

/**
 * 读取文章列表（支持多语言子目录）
 */
async function getArticles(dataDir: string, excludeId?: string, lang?: string) {
  const blogBaseDir = join(dataDir, 'blogs')

  // 支持的语言目录
  const langDirs = lang ? [lang] : ['en', 'fr', 'de']
  const articles: any[] = []

  for (const langDir of langDirs) {
    const blogDir = join(blogBaseDir, langDir)

    try {
      const files = await readdir(blogDir)
      const jsonFiles = files.filter(f => f.endsWith('.json'))

      for (const file of jsonFiles) {
        const id = file.replace('.json', '')
        if (id === excludeId) continue

        const content = await readFile(join(blogDir, file), 'utf8')
        const article = JSON.parse(content)
        articles.push({ id, ...article, _lang: langDir })
      }
    } catch {
      // 语言目录不存在时跳过
      continue
    }
  }

  return articles
}

export default defineEventHandler(async (event) => {
  try {
    const slugOrId = getRouterParam(event, 'id')
    if (!slugOrId) {
      throw createError({ statusCode: 400, statusMessage: 'Article ID or slug is required' })
    }

    const config = useRuntimeConfig(event)
    const dataDir = config.dataDir || getDataRoot()

    // 从查询参数获取语言，默认为 en
    const query = getQuery(event)
    const lang = (query.lang as string) || 'en'

    let currentArticle: any
    let currentArticleId: string = slugOrId  // 默认值，确保在使用前已赋值

    // ========== Slug-First 策略：优先使用 slug 查找 ==========
    // 原因：项目已全面迁移到 slug 路由系统
    const found = await findArticleBySlug(dataDir, slugOrId, lang)

    if (found) {
      // ✅ 通过 slug 找到（这是最常见的路径）
      currentArticle = found.data
      currentArticleId = found.id
    } else {
      // ❌ Slug 未找到，回退到 ID 查找（兼容旧链接）
      console.log(`🔍 Recommendations API: Not found by slug "${slugOrId}", trying ID fallback...`)
      const articlePathById = join(dataDir, 'blogs', lang, `${slugOrId}.json`)
      
      try {
        const content = await readFile(articlePathById, 'utf8')
        currentArticle = JSON.parse(content)
        currentArticleId = slugOrId
      } catch {
        // ID 也找不到，尝试其他语言目录
        for (const tryLang of ['en', 'fr', 'de']) {
          if (tryLang === lang) continue
          const foundInOtherLang = await findArticleBySlug(dataDir, slugOrId, tryLang)
          if (foundInOtherLang) {
            currentArticle = foundInOtherLang.data
            currentArticleId = foundInOtherLang.id
            break
          }
        }

        if (!currentArticle) {
          throw createError({ statusCode: 404, statusMessage: 'Article not found' })
        }
      }
    }

    // 分析文章内容
    const allTags = [
      ...(currentArticle.tags?.primary?.map((t: any) => t.name) || []),
      ...(currentArticle.tags?.primary?.map((t: any) => t.id) || []),
      ...(currentArticle.tags?.secondary?.map((t: any) => t.name) || []),
      ...(currentArticle.tags?.secondary?.map((t: any) => t.id) || [])
    ]

    const analysis = analyzeContent(
      currentArticle.overview?.title || '',
      currentArticle.overview?.excerpt || '',
      currentArticle.body?.content || '',
      allTags
    )

    // 加载文章数据（传入语言参数）
    const articles = await getArticles(dataDir, currentArticleId, lang)

    // 智能匹配相关文章
    const matchedArticles = articles
      .map(article => {
        const articleTags = [
          ...(article.tags?.primary?.map((t: any) => t.name) || []),
          ...(article.tags?.secondary?.map((t: any) => t.name) || [])
        ]

        // 计算相似度
        const tagScore = calculateTagSimilarity(allTags, articleTags)
        const countryScore = analysis.countries.includes(article.meta?.country) ? 0.5 : 0

        return {
          id: article.id,
          slug: article.meta?.slug || article.id,
          title: article.overview?.title || '',
          excerpt: article.overview?.excerpt || '',
          coverImage: article.visuals?.cover?.url || null,
          publishedAt: article.meta?.createdAt || '',
          link: `/blogs/${article.meta?.slug || article.id}`,
          score: tagScore + countryScore,
          country: article.meta?.country || ''
        }
      })
      .filter(a => a.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 5) // 最多5篇相关文章

    // 热门文章（按浏览量排序）
    const hotArticles = articles
      .filter(a => a.id !== currentArticleId)
      .sort((a, b) => (b.meta?.views || 0) - (a.meta?.views || 0))
      .slice(0, 5)
      .map(article => ({
        id: article.id,
        slug: article.meta?.slug || article.id,
        title: article.overview?.title || '',
        excerpt: article.overview?.excerpt || '',
        coverImage: article.visuals?.cover?.url || null,
        publishedAt: article.meta?.createdAt || '',
        link: `/blogs/${article.meta?.slug || article.id}`,
        views: article.meta?.views || 0
      }))

    // ========== Related Services & Partners (text similarity matching) ==========
    // Build source text from current blog article for matching
    const blogBodyText = typeof currentArticle.body === 'string'
      ? currentArticle.body
      : (currentArticle.body?.content || '')
    const blogSourceText = [
      currentArticle.seo?.keywords || '',
      currentArticle.seo?.keywords || '',
      currentArticle.seo?.keywords || '',
      currentArticle.overview?.title || '',
      currentArticle.overview?.title || '',
      currentArticle.overview?.excerpt || '',
      blogBodyText.slice(0, 800),
      allTags.join(' '),
      allTags.join(' ')
    ].join(' ').toLowerCase()

    const tokenize = (text: string): Set<string> => {
      return new Set(
        text.toLowerCase()
          .replace(/[^\w\s]/g, ' ')
          .split(/\s+/)
          .filter(t => t.length > 3)
      )
    }

    const blogTokens = tokenize(blogSourceText)
    const blogKeywordSet = new Set(
      (currentArticle.seo?.keywords || '')
        .toLowerCase()
        .split(/[,\s]+/)
        .map((k: string) => k.trim())
        .filter((k: string) => k.length > 2)
    )

    // Score service or partner against blog
    const scoreEntity = (entity: any): number => {
      const kw = (entity.seo?.keywords || '').toLowerCase()
      const desc = (entity.seo?.description || '').toLowerCase()
      const title = (entity.overview?.title || '').toLowerCase()
      const excerpt = (entity.overview?.excerpt || '').toLowerCase()
      const body = typeof entity.body === 'string' ? entity.body : (entity.body?.content || '')
      const bodyPreview = body.slice(0, 800).toLowerCase()

      const entityText = [kw, kw, kw, title, title, desc, excerpt, bodyPreview].join(' ')
      const entityTokens = tokenize(entityText)
      const entityKwSet = new Set(
        kw.split(/[,\s]+/).map((k: string) => k.trim()).filter((k: string) => k.length > 2)
      )

      // Keyword overlap score
      let kwScore = 0
      if (blogKeywordSet.size > 0 && entityKwSet.size > 0) {
        const kwIntersection = new Set([...blogKeywordSet].filter(k => entityKwSet.has(k)))
        kwScore = kwIntersection.size / Math.max(blogKeywordSet.size, entityKwSet.size)
      }

      // Text token overlap score
      let textScore = 0
      if (blogTokens.size > 0 && entityTokens.size > 0) {
        const textIntersection = new Set([...blogTokens].filter(t => entityTokens.has(t)))
        textScore = textIntersection.size / Math.max(blogTokens.size, entityTokens.size)
      }

      return kwScore * 0.5 + textScore * 0.5
    }

    const relatedServices: any[] = []
    const relatedPartners: any[] = []

    // Match services
    const servicesBaseDir = join(dataDir, 'services', lang)
    try {
      const serviceFiles = await readdir(servicesBaseDir)
      const servicesWithScores: any[] = []
      for (const file of serviceFiles.filter(f => f.endsWith('.json'))) {
        const content = await readFile(join(servicesBaseDir, file), 'utf8')
        const service = JSON.parse(content)
        const score = scoreEntity(service)
        if (score > 0.01) {
          const slug = service.meta?.slug || file.replace('.json', '')
          servicesWithScores.push({
            id: service.meta?.id || slug,
            title: service.overview?.title || '',
            excerpt: service.overview?.excerpt || '',
            coverImage: service.cover?.url || null,
            link: `/services/${slug}`,
            _score: score
          })
        }
      }
      servicesWithScores.sort((a, b) => b._score - a._score)
      relatedServices.push(...servicesWithScores.slice(0, 4).map(({ _score, ...rest }) => rest))
    } catch {}

    // Match partners
    const partnersBaseDir = join(dataDir, 'partners', lang)
    try {
      const partnerFiles = await readdir(partnersBaseDir)
      const partnersWithScores: any[] = []
      for (const file of partnerFiles.filter(f => f.endsWith('.json'))) {
        const content = await readFile(join(partnersBaseDir, file), 'utf8')
        const partner = JSON.parse(content)
        const score = scoreEntity(partner)
        if (score > 0.01) {
          const slug = partner.meta?.slug || file.replace('.json', '')
          partnersWithScores.push({
            id: partner.meta?.id || slug,
            title: partner.institution?.name || partner.overview?.title || '',
            excerpt: partner.overview?.excerpt || '',
            coverImage: partner.cover?.url || null,
            city: partner.meta?.city || '',
            type: partner.meta?.type || '',
            link: `/partners/${slug}`,
            _score: score
          })
        }
      }
      partnersWithScores.sort((a, b) => b._score - a._score)
      relatedPartners.push(...partnersWithScores.slice(0, 3).map(({ _score, ...rest }) => rest))
    } catch {}

    return {
      success: true,
      analysis: {
        detectedCountries: analysis.countries,
        detectedTopics: analysis.topics,
        recommendationTypes: analysis.relatedTypes
      },
      recommendations: {
        relatedArticles: matchedArticles,
        hotArticles: hotArticles,
        relatedServices,
        relatedPartners
      }
    }

  } catch (error: any) {
    if (error.statusCode) throw error

    console.error('Recommendations API error:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to get recommendations'
    })
  }
})
