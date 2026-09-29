import { createReadStream } from 'fs'
import { join } from 'path'
import { stat } from 'fs/promises'

function getDataRoot() {
  return join(process.cwd(), 'data')
}

export default defineEventHandler(async (event) => {
  const category = getRouterParam(event, 'category')
  const id = getRouterParam(event, 'id')
  const image = getRouterParam(event, 'image')

  if (!category || !id || !image) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing required parameters'
    })
  }

  if (!/^[\w-]+$/.test(id) || !/^[\w-]+$/.test(category)) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid id or category'
    })
  }

  const config = useRuntimeConfig(event)
  const dataDir = config.dataDir || getDataRoot()
  const filePath = join(dataDir, 'assets', 'products', category, id, image)

  try {
    const fileStats = await stat(filePath)
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
    const etag = `"${fileStats.mtimeMs.toString(16)}-${fileStats.size.toString(16)}"`
    setHeader(event, 'ETag', etag)
    setHeader(event, 'Cache-Control', 'public, max-age=86400, must-revalidate')
    setHeader(event, 'CDN-Cache-Control', 'public, max-age=31536000')

    const ifNoneMatch = getHeader(event, 'If-None-Match')
    if (ifNoneMatch === etag) {
      setResponseStatus(event, 304)
      return
    }

    return sendStream(event, createReadStream(filePath))
  } catch (error) {
    throw createError({
      statusCode: 404,
      statusMessage: 'Image not found'
    })
  }
})
