/**
 * Security Headers Nitro Plugin
 *
 * 1. Removes X-Powered-By: Nuxt (information leakage prevention)
 * 2. Sets Content-Language based on URL locale prefix (multi-language SEO)
 */
export default defineNitroPlugin((nitroApp) => {
  nitroApp.hooks.hook('render:response', (response, { event }) => {
    // Remove tech stack disclosure header
    delete response.headers['x-powered-by']

    // Determine locale from URL prefix for Content-Language
    const url = event.path || event.node.req.url || ''
    let lang = 'en'
    if (url.startsWith('/fr/') || url === '/fr') lang = 'fr'
    else if (url.startsWith('/de/') || url === '/de') lang = 'de'

    // Set Content-Language header for SEO
    response.headers['content-language'] = lang
  })
})
