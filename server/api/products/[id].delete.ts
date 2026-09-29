import { getQuery } from 'h3'
import { deleteEntity } from '../../utils/manageApi'

export default defineEventHandler(async (event) => {
  try {
    const id = getRouterParam(event, 'id')
    const query = getQuery(event)
    const lang = (query.lang as string) || 'en'

    if (!id) {
      throw createError({ statusCode: 400, statusMessage: 'Missing required field: id' })
    }

    const result = deleteEntity('product', lang, id)
    if (!result.success) {
      throw createError({ statusCode: 404, statusMessage: result.message })
    }

    return { success: true, message: result.message }
  } catch (error) {
    console.error('Error in product delete:', error)
    throw createError({ statusCode: 500, statusMessage: `Failed to delete: ${error instanceof Error ? error.message : String(error)}` })
  }
})
