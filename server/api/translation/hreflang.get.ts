import translationService from '~/server/utils/translationService'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const { contentId, category, currentLang, baseUrl } = query

  if (!contentId || !category) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing required parameters: contentId, category'
    })
  }

  try {
    const hreflangs = await translationService.generateHreflangs(
      contentId as string,
      category as string,
      (currentLang as string) || 'en',
      (baseUrl as string) || ''
    )

    return {
      success: true,
      data: hreflangs,
      count: hreflangs.length
    }
  } catch (error: any) {
    console.error('Hreflang generation error:', error)
    
    throw createError({
      statusCode: 500,
      statusMessage: error.message || 'Failed to generate hreflang tags'
    })
  }
})
