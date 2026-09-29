import { writeFileSync, mkdirSync } from 'fs'
import { join, extname } from 'path'

/**
 * 图片上传 API
 * 
 * 注意：此 API 需要 API Key 认证
 * 请在请求头中添加：Authorization: Bearer <your-api-key>
 * 
 * 认证中间件：server/middleware/auth.ts
 */

// 获取数据目录
function getDataDir(event: any): string {
  const config = useRuntimeConfig(event)
  return config.dataDir || join(process.cwd(), 'data')
}

// 验证文件类型
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
    // 获取表单数据
    const formData = await readMultipartFormData(event)

    if (!formData || formData.length === 0) {
      throw createError({
        statusCode: 400,
        statusMessage: 'No file uploaded'
      })
    }

    // 从表单数据中获取文件和参数
    let file: any = null
    let articleId: string = ''
    let filename: string = ''

    for (const field of formData) {
      if (field.name === 'file' && field.data) {
        file = field
      } else if (field.name === 'articleId') {
        articleId = field.data?.toString() || ''
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

    // 如果没有提供 articleId，使用时间戳创建临时目录
    if (!articleId) {
      articleId = `temp_${Date.now()}`
    }

    // 验证文件类型
    const mimeType = file.type || 'application/octet-stream'
    const originalName = file.filename || 'unnamed'
    const ext = extname(originalName).toLowerCase()

    if (!ALLOWED_MIME_TYPES.includes(mimeType) && !ALLOWED_EXTENSIONS.includes(ext)) {
      throw createError({
        statusCode: 400,
        statusMessage: `Invalid file type: ${mimeType}. Allowed types: ${ALLOWED_MIME_TYPES.join(', ')}`
      })
    }

    // 确定最终文件名
    const finalFilename = filename || originalName

    // 获取数据目录
    const dataDir = getDataDir(event)
    const uploadDir = join(dataDir, 'assets', 'blogs', articleId)

    // 创建目录
    mkdirSync(uploadDir, { recursive: true })

    // 保存文件
    const filePath = join(uploadDir, finalFilename)
    writeFileSync(filePath, file.data)

    console.log(`File uploaded: ${filePath}`)

    // 返回成功响应
    return {
      success: true,
      data: {
        articleId,
        filename: finalFilename,
        originalName,
        mimeType,
        size: file.data.length,
        url: `/api/assets/blogs/${articleId}/${finalFilename}`,
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
