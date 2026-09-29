import translationService from '~/server/utils/translationService'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const { slug, currentLang, category } = query

  if (!slug || !currentLang || !category) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing required parameters: slug, currentLang, category'
    })
  }

  try {
    const result = await translationService.getTargetUrl(
      slug as string,
      currentLang as string,
      (query.targetLang as string) || 'en',
      category as string
    )

    const translations: Record<string, string | null> = {}

    for (const lang of ['en', 'fr', 'de']) {
      const langResult = await translationService.getTargetUrl(
        slug as string,
        currentLang as string,
        lang,
        category as string
      )
      translations[lang] = langResult.targetUrl
    }

    return {
      success: true,
      data: result,
      translations,
      availableLanguages: result.availableLanguages,
      currentContent: {
        slug,
        lang: currentLang,
        category
      }
    }
  } catch (error: any) {
    console.error('Translation API error:', error)
    
    throw createError({
      statusCode: 500,
      statusMessage: error.message || 'Failed to process translation request'
    })
  }
})
