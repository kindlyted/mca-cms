import { readdirSync, readFileSync, existsSync } from 'fs'
import { join } from 'path'
import { getDataRoot } from './localizedData'
import { validateEntity } from './validation'

interface EntityConfig {
  dataDir: string
  entityType: 'service' | 'partner' | 'blog' | 'product'
  defaultSortBy: 'priority' | 'date' | 'title'
  categorySubdirs?: boolean
}

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  service: {
    dataDir: 'services',
    entityType: 'service',
    defaultSortBy: 'priority'
  },
  partner: {
    dataDir: 'partners',
    entityType: 'partner',
    defaultSortBy: 'priority'
  },
  blog: {
    dataDir: 'blogs',
    entityType: 'blog',
    defaultSortBy: 'date'
  },
  product: {
    dataDir: 'products',
    entityType: 'product',
    defaultSortBy: 'priority',
    categorySubdirs: true
  }
}

interface ListQueryParams {
  lang: string
  page: number
  pageSize: number
  keyword?: string
  tags?: string[]
  filters?: Record<string, string>
}

interface ApiResponse<T = any> {
  success: boolean
  data: T
  pagination?: {
    page: number
    pageSize: number
    total: number
    totalPages: number
  }
}

export function getEntityConfig(type: string): EntityConfig {
  const config = ENTITY_CONFIGS[type]
  if (!config) {
    throw new Error(`Unknown entity type: ${type}`)
  }
  return config
}

/**
 * Resolve the language-scoped directories to scan for an entity type.
 * Products live in per-category folders: data/products/{category}/{lang}
 */
function getEntityDirs(config: EntityConfig, dataRoot: string, lang: string): string[] {
  const baseDir = join(dataRoot, config.dataDir)

  if (config.categorySubdirs) {
    if (!existsSync(baseDir)) return []
    try {
      return readdirSync(baseDir, { withFileTypes: true })
        .filter(e => e.isDirectory())
        .map(e => join(baseDir, e.name, lang))
    } catch {
      return []
    }
  }

  return [join(baseDir, lang)]
}

export async function fetchEntityList(
  entityType: string,
  params: ListQueryParams
): Promise<ApiResponse> {
  const config = getEntityConfig(entityType)
  const dataRoot = getDataRoot()
  const entityDirs = getEntityDirs(config, dataRoot, params.lang).filter(dir => existsSync(dir))

  if (entityDirs.length === 0) {
    return {
      success: true,
      data: [],
      pagination: {
        page: params.page,
        pageSize: params.pageSize,
        total: 0,
        totalPages: 0
      }
    }
  }

  try {
    const entities: any[] = []
    for (const entityDir of entityDirs) {
      const files = readdirSync(entityDir).filter(f => f.endsWith('.json'))
      for (const file of files) {
        const content = readFileSync(join(entityDir, file), 'utf-8')
        entities.push(JSON.parse(content))
      }
    }

    let filtered = entities.filter(e => e.meta?.status === 'published')

    if (params.keyword) {
      const kw = params.keyword.toLowerCase()
      filtered = filtered.filter(e =>
        e.overview?.title?.toLowerCase().includes(kw) ||
        e.overview?.excerpt?.toLowerCase().includes(kw)
      )
    }

    if (params.tags && params.tags.length > 0) {
      const tagSet = new Set(params.tags)
      filtered = filtered.filter(e => {
        const allTags = [
          ...(e.tags?.primary || []),
          ...(e.tags?.secondary || [])
        ]
        return allTags.some((t: any) => tagSet.has(t.id))
      })
    }

    if (params.filters) {
      Object.entries(params.filters).forEach(([key, value]) => {
        if (value) {
          filtered = filtered.filter(e => {
            const keys = key.split('.')
            let val = e
            for (const k of keys) {
              val = val?.[k]
            }
            return val === value
          })
        }
      })
    }

    if (config.defaultSortBy === 'date') {
      filtered.sort((a, b) =>
        new Date(b.meta?.createdAt || '1970-01-01').getTime() -
        new Date(a.meta?.createdAt || '1970-01-01').getTime()
      )
    } else {
      filtered.sort((a, b) => (b.meta?.priority || 0) - (a.meta?.priority || 0))
    }

    const total = filtered.length
    const start = (params.page - 1) * params.pageSize
    const paginated = filtered.slice(start, start + params.pageSize)

    const listItems = paginated.map(entity =>
      transformToListItem(entityType, entity)
    )

    return {
      success: true,
      data: listItems,
      pagination: {
        page: params.page,
        pageSize: params.pageSize,
        total,
        totalPages: Math.ceil(total / params.pageSize)
      }
    }
  } catch (error) {
    console.error(`Error fetching ${entityType} list:`, error)
    throw error
  }
}

export async function fetchEntityById(
  entityType: string,
  id: string,
  lang: string
): Promise<ApiResponse> {
  const config = getEntityConfig(entityType)
  const dataRoot = getDataRoot()
  const entityDirs = getEntityDirs(config, dataRoot, lang).filter(dir => existsSync(dir))

  // ========== Slug-First 策略：URL param 对应 meta.slug ==========
  // 原因：sitemap 生成的 URL 使用 meta.slug，所以此处优先用 slug 匹配
  let filePath: string | null = null
  for (const entityDir of entityDirs) {
    filePath = await findBySlug(entityDir, id)
    if (filePath) break
  }

  if (!filePath) {
    // Slug 未找到，回退到 ID 查找（兼容旧链接和 meta.id 与 slug 一致的场景）
    for (const entityDir of entityDirs) {
      const fallbackPath = join(entityDir, `${id}.json`)
      if (existsSync(fallbackPath)) {
        filePath = fallbackPath
        break
      }
    }
    if (!filePath) {
      throw createError({
        statusCode: 404,
        statusMessage: `${entityType} not found: ${id}`
      })
    }
  }

  try {
    const content = readFileSync(filePath, 'utf-8')
    const entity = JSON.parse(content)

    if (entity.meta?.status !== 'published') {
      throw createError({
        statusCode: 404,
        statusMessage: `${entityType} not published`
      })
    }

    const validated = validateEntity(entityType, entity)
    if (!validated) {
      console.error(`⚠️  Validation failed for ${entityType}/${id}, returning raw data`)
    }

    // Add version param to /api/assets/... URLs for cache busting
    const base = validated || entity
    const version = base.meta?.updatedAt
    const resultEntity = version ? versionAssetUrls(base, version) : base

    return {
      success: true,
      data: resultEntity
    }
  } catch (error) {
    if ((error as any)?.code === 'ENOENT') {
      throw createError({
        statusCode: 404,
        statusMessage: `${entityType} not found: ${id}`
      })
    }
    console.error(`Error fetching ${entityType} by id:`, error)
    throw error
  }
}

// Helper: add ?v=version param to /api/assets/... image URLs for cache busting
function versionAssetUrl(s: string, version: string): string {
  if (typeof s !== 'string') return s
  if (!version) return s
  const v = encodeURIComponent(version)
  return s.replace(
    /\/api\/assets\/[\w\/.-]+?\.(webp|jpg|jpeg|png|gif)/gi,
    (match) => match.includes('?') ? match : `${match}?v=${v}`
  )
}

// Recursively walk an object/array/string and add version to /api/assets/ URLs
function versionAssetUrls(obj: any, version: string): any {
  if (obj == null) return obj
  if (typeof obj === 'string') return versionAssetUrl(obj, version)
  if (Array.isArray(obj)) return obj.map(item => versionAssetUrls(item, version))
  if (typeof obj === 'object') {
    const out: any = {}
    for (const k of Object.keys(obj)) {
      out[k] = versionAssetUrls(obj[k], version)
    }
    return out
  }
  return obj
}

function transformToListItem(entityType: string, entity: any): any {
  const rawImage = entity.cover?.url || entity.visuals?.thumbnail?.url || entity.visuals?.cover?.url
  const version = entity.meta?.updatedAt
  const base = {
    id: entity.meta?.id,
    slug: entity.meta?.slug || entity.meta?.id,
    title: entity.overview?.title,
    excerpt: entity.overview?.excerpt,
    image: versionAssetUrl(rawImage, version),
    featured: entity.meta?.featured,
    priority: entity.meta?.priority || 0
  }

  switch (entityType) {
    case 'service':
      return {
        ...base,
        category: entity.meta?.category,
        readTime: entity.meta?.readTime || 0,
        pricing: entity.pricing?.investment,
        description: entity.overview?.excerpt || entity.overview?.summary || ''
      }

    case 'product':
      return {
        ...base,
        category: entity.meta?.category,
        readTime: entity.meta?.readTime || 0,
        price: entity.price,
        compareAtPrice: entity.compareAtPrice,
        currency: entity.currency,
        inStock: entity.inStock,
        description: entity.overview?.excerpt || entity.overview?.summary || ''
      }

    case 'partner':
      return {
        ...base,
        type: entity.meta?.type,
        city: entity.meta?.city,
        region: entity.meta?.region,
        rating: entity.institution?.rating?.value,
        featured: entity.meta?.featured,
        priority: entity.meta?.priority || 0,
        description: entity.overview?.excerpt || entity.overview?.summary || ''
      }

    case 'blog':
      return {
        ...base,
        publishedAt: entity.meta?.createdAt,
        readTime: entity.meta?.readTime || 5,
        featured: entity.meta?.featured,
        priority: entity.meta?.priority || 0,
        tags: [
          ...(entity.tags?.primary || []),
          ...(entity.tags?.secondary || [])
        ].map((t: any) => ({ id: t.id, name: t.name }))
      }

    default:
      return base
  }
}

/**
 * Find entity file path by slug field
 * Searches all JSON files in directory for matching meta.slug
 */
async function findBySlug(dirPath: string, slug: string): Promise<string | null> {
  try {
    const files = readdirSync(dirPath).filter(f => f.endsWith('.json'))
    
    for (const file of files) {
      try {
        const filePath = join(dirPath, file)
        const content = readFileSync(filePath, 'utf-8')
        const entity = JSON.parse(content)
        
        if (entity.meta?.slug === slug) {
          if (process.env.NODE_ENV === 'development') console.log(`✅ Found by slug: ${slug} → ${file}`)
          return filePath
        }
      } catch (error) {
        // Skip invalid files
        continue
      }
    }
    
    if (process.env.NODE_ENV === 'development') console.log(`❌ Slug not found: "${slug}" in ${files.length} files`)
    return null
  } catch (error) {
    console.error('Error searching by slug:', error)
    return null
  }
}
