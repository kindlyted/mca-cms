export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { password } = body

  // 从环境变量获取管理员密码，如果没有设置则使用默认密码
  const adminPassword = process.env.ADMIN_PASSWORD || 'admin123'

  if (password === adminPassword) {
    // 生成一个简单的token（生产环境应该使用JWT）
    const token = Buffer.from(`admin:${Date.now()}`).toString('base64')

    return {
      success: true,
      message: '登录成功',
      token: token
    }
  } else {
    throw createError({
      statusCode: 401,
      statusMessage: '密码错误'
    })
  }
})