import { getQuery } from 'h3'
import { fetchEntityList } from '../../utils/contentApi'

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event)
    const result = await fetchEntityList('product', {
      lang: (query.lang as string) || 'en',
      page: Number(query.page) || 1,
      pageSize: Number(query.pageSize) || 12,
      keyword: query.keyword as string,
      filters: {
        'meta.category': query.category as string
      }
    })
    return result
  } catch (error) {
    console.error('Error fetching products:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to fetch products'
    })
  }
})
