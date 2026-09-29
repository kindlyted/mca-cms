import { readdirSync, readFileSync, existsSync } from 'fs'
import { join } from 'path'
import { getDataRoot } from './localizedData'

export interface TranslationMap {
  [lang: string]: string | null  // lang → slug (null 表示该语言不存在)
}

interface CacheEntry {
  translations: TranslationMap
  timestamp: number
}

export interface HrefLangTag {
  lang: string
  url: string
}

export interface LanguageSwitchResult {
  success: boolean
  targetUrl: string | null
  fallbackUrl?: string
  availableLanguages: string[]
  message?: string
}

const SUPPORTED_LANGUAGES = ['en', 'fr', 'de']
const CACHE_TTL = 5 * 60 * 1000  // 5 分钟缓存

type LanguageSlugMap = Map<string, string>  // lang → slug
type EntityTypeIndex = Map<string, LanguageSlugMap>  // id → {lang: slug}

class TranslationService {
  private cache: Map<string, CacheEntry> = new Map()
  private idIndex: Map<string, EntityTypeIndex> = new Map()  // entityType → (id → {lang: slug})
  private indexBuilt = false
  private customDataRoot?: string

  constructor(dataRoot?: string) {
    console.log('🌐 TranslationService initialized')
    this.customDataRoot = dataRoot
  }

  async buildIndex(): Promise<void> {
    if (this.indexBuilt) {
      return
    }

    let dataRoot: string
    if (this.customDataRoot) {
      dataRoot = this.customDataRoot
    } else {
      try {
        dataRoot = getDataRoot()
      } catch (error) {
        dataRoot = join(process.cwd(), 'data')
      }
    }

    const entityTypes = ['products', 'services', 'partners', 'blogs']

    for (const type of entityTypes) {
      const typeIndex: EntityTypeIndex = new Map()

      for (const lang of SUPPORTED_LANGUAGES) {
        let dirPaths: string[]

        if (type === 'products') {
          // products 按分类子目录组织: data/products/{category}/{lang}
          const productsBase = join(dataRoot, 'products')
          if (!existsSync(productsBase)) {
            continue
          }
          dirPaths = readdirSync(productsBase, { withFileTypes: true })
            .filter(e => e.isDirectory())
            .map(e => join(productsBase, e.name, lang))
        } else {
          dirPaths = [join(dataRoot, type, lang)]
        }

        for (const dirPath of dirPaths) {
          if (!existsSync(dirPath)) {
            continue
          }

          try {
            const files = readdirSync(dirPath).filter(f => f.endsWith('.json'))

            for (const file of files) {
              try {
                const filePath = join(dirPath, file)
                const content = readFileSync(filePath, 'utf-8')
                const entity = JSON.parse(content)

                if (entity.meta?.id && entity.meta?.slug) {
                  const id = entity.meta.id
                  const slug = entity.meta.slug

                  if (!typeIndex.has(id)) {
                    typeIndex.set(id, new Map())
                  }

                  typeIndex.get(id)!.set(lang, slug)
                }
              } catch (error) {
                console.warn(`⚠️  Failed to parse ${file}:`, error)
              }
            }
          } catch (error) {
            console.warn(`⚠️  Failed to read directory ${dirPath}:`, error)
          }
        }
      }

      this.idIndex.set(type, typeIndex)
    }

    this.indexBuilt = true
    const totalEntries = Array.from(this.idIndex.values()).reduce(
      (sum, map) => sum + map.size, 0
    )
    console.log(`✅ Translation index built: ${totalEntries} entities indexed`)
  }

  async getTranslationMap(
    entityType: string,
    contentId: string
  ): Promise<TranslationMap | null> {
    await this.buildIndex()

    const cacheKey = `${entityType}:${contentId}`

    const cached = this.cache.get(cacheKey)
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return cached.translations
    }

    const typeIndex = this.idIndex.get(entityType)
    if (!typeIndex) {
      console.error(`❌ Unknown entity type: ${entityType}`)
      return null
    }

    const langMap: LanguageSlugMap | undefined = typeIndex.get(contentId)
    if (!langMap) {
      console.warn(`⚠️  No content found with ID: ${contentId}`)
      return null
    }

    const translations: TranslationMap = {}

    for (const lang of SUPPORTED_LANGUAGES) {
      translations[lang] = langMap.get(lang) || null
    }

    this.cache.set(cacheKey, {
      translations,
      timestamp: Date.now()
    })

    return translations
  }

  async getTargetUrl(
    currentSlug: string,
    currentLang: string,
    targetLang: string,
    category: string
  ): Promise<LanguageSwitchResult> {
    await this.buildIndex()

    const entityType = this.normalizeEntityType(category)
    const contentId = await this.findContentIdBySlug(entityType, currentSlug, currentLang)

    if (!contentId) {
      return {
        success: false,
        targetUrl: null,
        availableLanguages: [],
        message: `Content not found: ${currentSlug} in ${currentLang}`
      }
    }

    const translationMap = await this.getTranslationMap(entityType, contentId)
    
    if (!translationMap) {
      return {
        success: false,
        targetUrl: null,
        availableLanguages: [],
        message: `Translation map not found for ID: ${contentId}`
      }
    }

    const targetSlug = translationMap[targetLang]
    const availableLanguages = Object.entries(translationMap)
      .filter(([, slug]) => slug !== null)
      .map(([lang]) => lang)

    if (targetSlug) {
      const routeCategory = this.getRouteCategory(entityType)
      const prefix = targetLang === 'en' ? '' : `/${targetLang}`
      return {
        success: true,
        targetUrl: `${prefix}/${routeCategory}/${targetSlug}`,
        availableLanguages,
        message: `Successfully found ${targetLang} version`
      }
    }

    let fallbackUrl: string | undefined
    let message: string

    if (entityType === 'blogs') {
      const blogPath = targetLang === 'en' ? '/blogs' : `/${targetLang}/blogs`
      fallbackUrl = blogPath
      message = `No ${targetLang} version available for this blog post. Redirecting to blog listing.`
    } else {
      message = `ERROR: Missing ${targetLang} translation for ${entityType}/${contentId}. This should not happen!`
      console.error(`🚨 ${message}`)
    }

    return {
      success: false,
      targetUrl: null,
      fallbackUrl,
      availableLanguages,
      message
    }
  }

  async generateHreflangs(
    contentId: string,
    category: string,
    currentLang: string,
    baseUrl: string = ''
  ): Promise<HrefLangTag[]> {
    await this.buildIndex()

    const entityType = this.normalizeEntityType(category)
    const translationMap = await this.getTranslationMap(entityType, contentId)

    if (!translationMap) {
      console.warn(`⚠️  Cannot generate hreflangs for ID: ${contentId}`)
      return []
    }

    const tags: HrefLangTag[] = []
    const routeCategory = this.getRouteCategory(entityType)

    for (const lang of SUPPORTED_LANGUAGES) {
      const slug = translationMap[lang]

      if (slug) {
        const langPrefix = lang === 'en' ? '' : `/${lang}`
        tags.push({
          lang,
          url: `${baseUrl}${langPrefix}/${routeCategory}/${slug}`
        })
      } else if (entityType === 'blogs') {
        const blogPrefix = lang === 'en' ? '' : `/${lang}`
        tags.push({
          lang,
          url: `${baseUrl}${blogPrefix}/blogs`
        })
      }
    }

    const defaultSlug = translationMap[currentLang] || translationMap['en']
    if (defaultSlug) {
      tags.push({
        lang: 'x-default',
        url: `${baseUrl}/${routeCategory}/${defaultSlug}`
      })
    }

    return tags
  }

  async getAllTranslationsForEntity(
    entityType: string,
    contentId: string
  ): Promise<{ lang: string; slug: string; url: string }[]> {
    await this.buildIndex()

    const translationMap = await this.getTranslationMap(entityType, contentId)
    
    if (!translationMap) {
      return []
    }

    const category = this.getRouteCategory(entityType)
    const results: { lang: string; slug: string; url: string }[] = []

    for (const [lang, slug] of Object.entries(translationMap)) {
      if (slug) {
        const langPrefix = lang === 'en' ? '' : `/${lang}`
        results.push({
          lang,
          slug,
          url: `${langPrefix}/${category}/${slug}`
        })
      }
    }

    return results
  }

  clearCache(): void {
    this.cache.clear()
    console.log('🗑️  Translation cache cleared')
  }

  rebuildIndex(): void {
    this.indexBuilt = false
    this.idIndex.clear()
    this.cache.clear()
    console.log('🔄 Translation index marked for rebuild')
  }

  getCacheStats(): { size: number; entries: number } {
    return {
      size: this.cache.size,
      entries: Array.from(this.idIndex.values()).reduce((sum, map) => sum + map.size, 0)
    }
  }

  private normalizeEntityType(category: string): string {
    const mapping: Record<string, string> = {
      'services': 'services',
      'partners': 'partners',
      'products': 'products',
      'blogs': 'blogs',
      'blog': 'blogs'
    }
    return mapping[category] || category
  }

  private getEntityCategory(entityType: string): string {
    const mapping: Record<string, string> = {
      'services': 'services',
      'partners': 'partners',
      'products': 'products',
      'blogs': 'blogs'
    }
    return mapping[entityType] || entityType
  }

  private getRouteCategory(entityType: string): string {
    const mapping: Record<string, string> = {
      'services': 'services',
      'partners': 'partners',
      'products': 'products',
      'blogs': 'blogs'
    }
    return mapping[entityType] || entityType
  }

  private async findContentIdBySlug(
    entityType: string,
    slug: string,
    lang: string
  ): Promise<string | null> {
    await this.buildIndex()

    const typeIndex = this.idIndex.get(entityType)
    if (!typeIndex) {
      return null
    }

    for (const [id, langMap] of typeIndex.entries()) {
      const slugMap: LanguageSlugMap = langMap
      if (slugMap.get(lang) === slug) {
        return id
      }
    }

    return null
  }
}

export const translationService = new TranslationService()

export default translationService
export { TranslationService }
