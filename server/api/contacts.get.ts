import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default defineEventHandler(async (event) => {
  // 使用Authorization header进行token认证
  const authHeader = getHeader(event, 'authorization')
  const token = authHeader?.replace('Bearer ', '')

  if (!token) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized - No token provided'
    })
  }

  // 简单的token验证（生产环境应该使用JWT）
  try {
    const decoded = Buffer.from(token, 'base64').toString('ascii')
    if (!decoded.startsWith('admin:')) {
      throw new Error('Invalid token')
    }
  } catch (error) {
    throw createError({
      statusCode: 401,
      statusMessage: 'Unauthorized - Invalid token'
    })
  }

  try {
    const contacts = await prisma.contact.findMany({
      orderBy: {
        submittedAt: 'desc'
      }
    })

    return {
      success: true,
      data: contacts
    }
  } catch (error) {
    console.error('获取联系信息失败:', error)
    return {
      success: false,
      error: '获取数据失败'
    }
  }
})