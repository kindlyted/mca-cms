import { writeFileSync, mkdirSync } from 'fs'
import { join, extname } from 'path'

/**
 * Product 图片上传 API
 *
 * 需要 API Key 认证
 * 请求头：Authorization: Bearer <your-api-key>
 */

function getDataDir(event: any): string {
  const config = useRuntimeConfig(event)
  return config.dataDir || join(process.cwd(), 'data')
}

const ALLOWED_MIME_TYPES = [
  'image/jpeg',
  'image/jpg',
  'image/png',
  'image/webp',
  'image/gif'
]

const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']

export default defineEventHandler(async (event) => {
  try {
    const formData = await readMultipartFormData(event)

    if (!formData || formData.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No file uploaded'
      })
    }

    let file: any = null
    let productId: string = ''
    let category: string = ''
    let filename: string = ''

    for (const field of formData) {
      if (field.name === 'file' && field.data) {
        file = field
      } else if (field.name === 'productId') {
        productId = field.data?.toString() || ''
      } else if (field.name === 'category') {
        category = field.data?.toString() || ''
      } else if (field.name === 'filename') {
        filename = field.data?.toString() || ''
      }
    }

    if (!file) {
      throw createError({
        statusCode: 400,
        statusMessage: 'File field is required'
      })
    }

    if (!productId) {
      productId = `temp_${Date.now()}`
    }
    if (!category) {
      category = 'general'
    }

    const mimeType = file.type || 'application/octet-stream'
    const originalName = file.filename || 'unnamed'
    const ext = extname(originalName).toLowerCase()

    if (!ALLOWED_MIME_TYPES.includes(mimeType) && !ALLOWED_EXTENSIONS.includes(ext)) {
      throw createError({
        statusCode: 400,
        statusMessage: `Invalid file type: ${mimeType}. Allowed types: ${ALLOWED_MIME_TYPES.join(', ')}`
      })
    }

    const finalFilename = filename || originalName
    const dataDir = getDataDir(event)
    const uploadDir = join(dataDir, 'assets', 'products', category, productId)

    mkdirSync(uploadDir, { recursive: true })

    const filePath = join(uploadDir, finalFilename)
    writeFileSync(filePath, file.data)

    console.log(`File uploaded: ${filePath}`)

    return {
      success: true,
      data: {
        productId,
        category,
        filename: finalFilename,
        originalName,
        mimeType,
        size: file.data.length,
        url: `/api/assets/products/${category}/${productId}/${finalFilename}`,
        path: filePath
      }
    }
  } catch (error: any) {
    console.error('Upload API error:', error)

    if (error.statusCode) {
      throw error
    }

    throw createError({
      statusCode: 500,
      statusMessage: `Upload failed: ${error.message}`
    })
  }
})
