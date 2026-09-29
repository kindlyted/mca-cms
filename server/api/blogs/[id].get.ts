import { getRouterParam, createError } from 'h3'
import { fetchEntityById } from '../../utils/contentApi'

export default defineEventHandler(async (event) => {
  try {
    const id = getRouterParam(event, 'id')
    if (!id) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Blog ID is required'
      })
    }

    const query = getQuery(event)
    const result = await fetchEntityById('blog', id, (query.lang as string) || 'en')
    return result
  } catch (error) {
    console.error('Error fetching blog:', error)
    throw error
  }
})
