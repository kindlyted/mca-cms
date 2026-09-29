import { createReadStream } from 'fs'
import { join } from 'path'
import { stat } from 'fs/promises'

// 获取项目根目录的辅助函数
function getDataRoot() {
  return join(process.cwd(), 'data')
}

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const image = getRouterParam(event, 'image')

  // 验证参数
  if (!id || !image) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing required parameters'
    })
  }

  // 安全检查：只允许字母、数字、连字符和下划线
  if (!/^[\w-]+$/.test(id)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid id'
    })
  }

  // 获取数据目录：优先使用配置，否则使用相对路径
  const config = useRuntimeConfig(event)
  const dataDir = config.dataDir || getDataRoot()

  // 构建文件路径
  const filePath = join(dataDir, 'assets', 'blogs', id, image)

  try {
    // 检查文件是否存在
    const fileStats = await stat(filePath)

    // 根据文件扩展名设置Content-Type
    const ext = image.split('.').pop()?.toLowerCase() || 'jpg'
    const contentTypeMap: Record<string, string> = {
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'webp': 'image/webp',
      'png': 'image/png',
      'gif': 'image/gif'
    }
    const contentType = contentTypeMap[ext] || 'image/jpeg'

    setHeader(event, 'Content-Type', contentType)
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
