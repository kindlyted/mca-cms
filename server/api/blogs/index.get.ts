import { getQuery } from 'h3'
import { fetchEntityList } from '../../utils/contentApi'

export default defineEventHandler(async (event) => {
  try {
    const query = getQuery(event)
    const tagsParam = query.tags as string | undefined
    const result = await fetchEntityList('blog', {
      lang: (query.lang as string) || 'en',
      page: Number(query.page) || 1,
      pageSize: Number(query.pageSize) || 12,
      keyword: query.keyword as string,
      tags: tagsParam ? tagsParam.split(',').filter(Boolean) : undefined,
      filters: {}
    })
    return result
  } catch (error) {
    console.error('Error fetching blogs:', error)
    throw createError({
      statusCode: 500,
      statusMessage: `Failed to fetch blogs: ${error instanceof Error ? error.message : String(error)}`
    })
  }
})
