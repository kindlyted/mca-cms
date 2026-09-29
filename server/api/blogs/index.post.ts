import { writeFileSync, mkdirSync } from 'fs'
import { join, extname, basename } from 'path'
import { saveEntity } from '../../utils/manageApi'

function getDataDir(event: any): string {
  const config = useRuntimeConfig(event)
  return config.dataDir || join(process.cwd(), 'data')
}

function generateArticleId(): string {
  const timestamp = Date.now()
  const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0')
  return `${timestamp}${random}`
}

async function downloadImage(url: string): Promise<Buffer | null> {
  try {
    const response = await fetch(url)
    if (!response.ok) return null
    const arrayBuffer = await response.arrayBuffer()
    return Buffer.from(arrayBuffer)
  } catch { return null }
}

function decodeBase64Image(base64String: string): { buffer: Buffer; ext: string } | null {
  try {
    const matches = base64String.match(/^data:image\/([a-zA-Z]+);base64,(.+)$/)
    if (matches) return { buffer: Buffer.from(matches[2], 'base64'), ext: matches[1] }
    return { buffer: Buffer.from(base64String, 'base64'), ext: 'png' }
  } catch { return null }
}

async function saveImage(imageData: string, articleDir: string, filename: string): Promise<string | null> {
  try {
    let buffer: Buffer | null = null
    let ext = extname(filename).slice(1) || 'jpg'
    if (imageData.startsWith('http://') || imageData.startsWith('https://')) {
      buffer = await downloadImage(imageData)
      const urlExt = extname(new URL(imageData).pathname).slice(1)
      if (urlExt) ext = urlExt
    } else if (imageData.startsWith('data:image')) {
      const decoded = decodeBase64Image(imageData)
      if (decoded) { buffer = decoded.buffer; ext = decoded.ext }
    }
    if (!buffer) return null
    const finalFilename = `${basename(filename, extname(filename))}.${ext}`
    writeFileSync(join(articleDir, finalFilename), buffer)
    return finalFilename
  } catch { return null }
}

async function processImages(articleData: any, articleId: string, dataDir: string): Promise<{ success: boolean; errors: string[] }> {
  const errors: string[] = []
  const articleDir = join(dataDir, 'assets', 'blogs', articleId)
  try { mkdirSync(articleDir, { recursive: true }) } catch { errors.push('Failed to create directory: ' + articleDir); return { success: false, errors } }

  const processUrl = async (url: string | undefined, destName: string, prefix: string) => {
    if (!url || url.startsWith('/api/assets/')) return url
    const saved = await saveImage(url, articleDir, destName)
    if (saved) return '/api/assets/' + prefix + '/' + articleId + '/' + saved
    errors.push('Failed to save image: ' + destName)
    return url
  }

  if (articleData.visuals?.cover?.url) articleData.visuals.cover.url = (await processUrl(articleData.visuals.cover.url, 'cover.jpg', 'blogs')) || articleData.visuals.cover.url
  if (articleData.visuals?.thumbnail?.url) articleData.visuals.thumbnail.url = (await processUrl(articleData.visuals.thumbnail.url, 'thumbnail.jpg', 'blogs')) || articleData.visuals.thumbnail.url

  if (articleData.visuals?.gallery && Array.isArray(articleData.visuals.gallery)) {
    for (let i = 0; i < articleData.visuals.gallery.length; i++) {
      const item = articleData.visuals.gallery[i]
      if (item.url) item.url = (await processUrl(item.url, String(i + 1).padStart(2, '0') + '.jpg', 'blogs')) || item.url
    }
  }

  if (articleData.body?.content) {
    const imgRegex = /!\[([^\]]*)\]\(([^)]+)\)/g
    let match; let imgIndex = 0
    const contentImages: Map<string, string> = new Map()
    while ((match = imgRegex.exec(articleData.body.content)) !== null) {
      const imgUrl = match[2]
      if (!imgUrl.startsWith('/api/assets/') && !contentImages.has(imgUrl)) {
        imgIndex++
        const saved = await saveImage(imgUrl, articleDir, 'content_' + String(imgIndex).padStart(2, '0') + '.jpg')
        if (saved) contentImages.set(imgUrl, '/api/assets/blogs/' + articleId + '/' + saved)
        else errors.push('Failed to save content image: ' + imgUrl)
      }
    }
    contentImages.forEach((newUrl, oldUrl) => {
      articleData.body.content = articleData.body.content.replace(new RegExp('\\(', 'g'), '(').replace(new RegExp('\\)', 'g'), ')')
      // Safer replacement using split-join
      articleData.body.content = articleData.body.content.split('(' + oldUrl + ')').join('(' + newUrl + ')')
    })
  }

  if (articleData.seo?.og?.image && !articleData.seo.og.image.startsWith('/api/assets/') && !articleData.seo.og.image.startsWith('http')) articleData.seo.og.image = '/api/assets/blogs/' + articleId + '/cover.jpg'
  if (articleData.seo?.twitter?.image && !articleData.seo.twitter.image.startsWith('/api/assets/') && !articleData.seo.twitter.image.startsWith('http')) articleData.seo.twitter.image = '/api/assets/blogs/' + articleId + '/cover.jpg'

  return { success: errors.length === 0, errors }
}

function validateArticleData(data: any): { valid: boolean; errors: string[] } {
  const errors: string[] = []
  if (!data) return { valid: false, errors: ['Article data is required'] }
  if (!data.meta) errors.push('meta is required')
  if (!data.overview) errors.push('overview is required')
  if (!data.overview?.title) errors.push('overview.title is required')
  if (!data.body?.content) errors.push('body.content is required')
  if (!data.meta?.id) { data.meta = data.meta || {}; data.meta.id = generateArticleId() }
  if (!data.meta.status) data.meta.status = 'published'
  if (!data.meta.language) data.meta.language = 'zh-CN'
  if (!data.meta?.createdAt) data.meta.createdAt = new Date().toISOString()
  if (!data.meta?.updatedAt) data.meta.updatedAt = new Date().toISOString()
  return { valid: errors.length === 0, errors }
}

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event)
    if (!body) throw createError({ statusCode: 400, statusMessage: 'Request body is required' })
    const articleData = body.article || body
    const validation = validateArticleData(articleData)
    if (!validation.valid) throw createError({ statusCode: 400, statusMessage: 'Validation failed: ' + validation.errors.join(', ') })

    const articleId = articleData.meta.id
    const dataDir = getDataDir(event)
    const imageResult = await processImages(articleData, articleId, dataDir)
    if (!imageResult.success) console.warn('Image processing warnings:', imageResult.errors)

    const lang = articleData.meta.language || 'en'
    const saveResult = saveEntity('blog', lang, articleData)
    if (!saveResult.success) throw createError({ statusCode: 500, statusMessage: 'Failed to save article: ' + saveResult.message })

    return {
      success: true, data: {
        id: articleId, slug: articleData.meta?.slug || articleId, title: articleData.overview.title,
        url: '/blogs/' + (articleData.meta?.slug || articleId),
        apiUrl: '/api/blogs/' + articleId,
        publishedAt: articleData.meta?.createdAt,
        imageErrors: imageResult.errors.length > 0 ? imageResult.errors : undefined
      }
    }
  } catch (error: any) {
    console.error('Blog management API error:', error)
    if (error.statusCode) throw error
    throw createError({ statusCode: 500, statusMessage: 'Internal server error: ' + error.message })
  }
})
