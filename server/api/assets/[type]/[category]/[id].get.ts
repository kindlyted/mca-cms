import { createReadStream } from 'fs'
import { join } from 'path'
import { stat } from 'fs/promises'
import { fileURLToPath } from 'url'
import { dirname } from 'path'

// 获取项目根目录的辅助函数
function getDataRoot() {
  const __filename = fileURLToPath(import.meta.url)
  const __dirname = dirname(__filename)
  return join(__dirname, '../../../..')
}

export default defineEventHandler(async (event) => {
  const type = getRouterParam(event, 'type')
  const category = getRouterParam(event, 'category')
  const id = getRouterParam(event, 'id')

  // 验证参数
  if (!type || !category || !id) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing required parameters'
    })
  }

  // 安全检查：只允许特定路径
  const allowedTypes = ['services', 'blog']
  const allowedCategories: Record<string, string[]> = {
    services: ['cards', 'home', 'detail'],
    blog: ['cover', 'content']
  }

  if (!allowedTypes.includes(type)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid type'
    })
  }

  if (!allowedCategories[type]?.includes(category)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid category'
    })
  }

  // 获取数据目录：优先使用配置，否则使用相对路径
  const config = useRuntimeConfig(event)
  const dataDir = config.dataDir || getDataRoot()

  // 构建文件路径
  const filePath = join(dataDir, 'assets', type, category, id)

  try {
    // 检查文件是否存在
    const fileStats = await stat(filePath)

    // 设置响应头
    setHeader(event, 'Content-Type', 'image/webp')
    // 使用 ETag 和较短的缓存时间，允许缓存验证
    const etag = `"${fileStats.mtimeMs.toString(16)}-${fileStats.size.toString(16)}"`
    setHeader(event, 'ETag', etag)
    setHeader(event, 'Cache-Control', 'public, max-age=86400, must-revalidate')
    setHeader(event, 'CDN-Cache-Control', 'public, max-age=31536000')

    // 支持条件请求：如果 ETag 匹配，返回 304 Not Modified
    const ifNoneMatch = getHeader(event, 'If-None-Match')
    if (ifNoneMatch === etag) {
      setResponseStatus(event, 304)
      return
    }

    // 返回文件流
    return sendStream(event, createReadStream(filePath))
  } catch (error) {
    throw createError({
      statusCode: 404,
      statusMessage: 'Image not found'
    })
  }
})
