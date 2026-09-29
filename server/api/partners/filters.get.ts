import { readdirSync, readFileSync, existsSync } from 'fs'
import { join } from 'path'
import { getDataRoot } from '../../utils/localizedData'

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event)
    const lang = (query.lang as string) || 'en'
    const dataRoot = getDataRoot()
    const entityDir = join(dataRoot, 'partners', lang)

    if (!existsSync(entityDir)) {
      return { success: true, data: { types: [], cities: [] } }
    }

    const files = readdirSync(entityDir).filter(f => f.endsWith('.json'))
    const types = new Set<string>()
    const cities = new Set<string>()

    for (const file of files) {
      try {
        const content = readFileSync(join(entityDir, file), 'utf-8')
        const entity = JSON.parse(content)
        if (entity.meta?.status !== 'published') continue
        if (entity.meta?.type) types.add(entity.meta.type)
        if (entity.meta?.city) cities.add(entity.meta.city)
      } catch {
        continue
      }
    }

    return {
      success: true,
      data: {
        types: Array.from(types).sort(),
        cities: Array.from(cities).sort()
      }
    }
  } catch (error) {
    console.error('Error fetching partner filters:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to fetch partner filters'
    })
  }
})
