import { readdirSync, readFileSync, existsSync } from 'fs'
import { join } from 'path'
import { getDataRoot } from '../../utils/localizedData'

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event)
    const lang = (query.lang as string) || 'en'
    const dataRoot = getDataRoot()
    const productsDir = join(dataRoot, 'products')

    if (!existsSync(productsDir)) {
      return { success: true, data: { categories: [] } }
    }

    // products 按 data/products/{category}/{lang} 分目录存储，
    // 每个一级子目录即一个分类。遍历子目录并统计已发布商品数量。
    const categories: Array<{ id: string; count: number }> = []

    const categoryDirs = readdirSync(productsDir, { withFileTypes: true })
      .filter(e => e.isDirectory())
      .map(e => e.name)
      .sort()

    for (const cat of categoryDirs) {
      const langDir = join(productsDir, cat, lang)
      if (!existsSync(langDir)) continue

      let count = 0
      const files = readdirSync(langDir).filter(f => f.endsWith('.json'))
      for (const file of files) {
        try {
          const content = readFileSync(join(langDir, file), 'utf-8')
          const entity = JSON.parse(content)
          if (entity.meta?.status === 'published') count++
        } catch {
          continue
        }
      }

      if (count > 0) {
        categories.push({ id: cat, count })
      }
    }

    return {
      success: true,
      data: { categories }
    }
  } catch (error) {
    console.error('Error fetching product filters:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to fetch product filters'
    })
  }
})
