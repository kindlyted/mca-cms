import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

interface ContactForm {
  name: string
  phone: string
  email: string
  type: string
  message: string
  userAgent?: string
  browserLanguage?: string
  platform?: string
  screenResolution?: string
  timezone?: string
}

export default defineEventHandler(async (event) => {
  try {
    const body = await readBody(event) as ContactForm

    if (!body.name || !body.email || !body.message) {
      return {
        success: false,
        error: '请填写必填字段'
      }
    }

    // Get client IP from request headers
    const forwarded = getHeader(event, 'x-forwarded-for')
    const ip = forwarded?.split(',')[0]?.trim() || event.node.req.socket.remoteAddress || null

    // 保存到数据库
    const contact = await prisma.contact.create({
      data: {
        name: body.name,
        phone: body.phone,
        email: body.email,
        type: body.type || null,
        message: body.message,
        userAgent: body.userAgent || null,
        browserLanguage: body.browserLanguage || null,
        platform: body.platform || null,
        screenResolution: body.screenResolution || null,
        timezone: body.timezone || null,
        ipAddress: ip
      }
    })

    return {
      success: true,
      message: '咨询已提交，我们会尽快与您联系！',
      contactId: contact.id
    }
  } catch (error) {
    console.error('保存咨询失败:', error)
    return {
      success: false,
      error: '保存失败，请稍后重试或直接联系我们'
    }
  }
})
