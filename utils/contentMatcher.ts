/**
 * Content matching utility for blog articles
 * Analyzes article content to extract matching information
 */

/**
 * Country/region keywords for matching
 */
const countryKeywords: Record<string, string[]> = {
  china: ['中国', 'china', 'chinese', 'beijing', 'beijing', 'shanghai', 'shanghai', 'guangzhou', 'shenzhen'],
  usa: ['美国', 'usa', 'united states', 'america', 'american'],
  uk: ['英国', 'uk', 'united kingdom', 'britain', 'british', 'england'],
  canada: ['加拿大', 'canada', 'canadian'],
  australia: ['澳大利亚', 'australia', 'australian'],
  japan: ['日本', 'japan', 'japanese', 'tokyo'],
  singapore: ['新加坡', 'singapore', 'singaporean'],
  thailand: ['泰国', 'thailand', 'thai', 'bangkok'],
  malaysia: ['马来西亚', 'malaysia', 'malaysian', 'kuala lumpur'],
  germany: ['德国', 'germany', 'german'],
  france: ['法国', 'france', 'french'],
  switzerland: ['瑞士', 'switzerland', 'swiss']
}

/**
 * Topic keywords for matching
 * Left empty for a neutral template — related-content matching relies on
 * tag similarity instead of domain-specific topic extraction.
 */
const topicKeywords: Record<string, string[]> = {}

/**
 * Extract countries mentioned in text
 */
function extractCountries(text: string): string[] {
  const lowerText = text.toLowerCase()
  const foundCountries: string[] = []

  for (const [country, keywords] of Object.entries(countryKeywords)) {
    if (keywords.some(kw => lowerText.includes(kw.toLowerCase()))) {
      foundCountries.push(country)
    }
  }

  return foundCountries
}

/**
 * Extract topics mentioned in text
 */
function extractTopics(text: string): string[] {
  const lowerText = text.toLowerCase()
  const foundTopics: string[] = []

  for (const [topic, keywords] of Object.entries(topicKeywords)) {
    if (keywords.some(kw => lowerText.includes(kw.toLowerCase()))) {
      foundTopics.push(topic)
    }
  }

  return foundTopics
}

/**
 * Calculate Jaccard similarity between two sets
 */
function jaccardSimilarity(setA: Set<string>, setB: Set<string>): number {
  const intersection = new Set([...setA].filter(x => setB.has(x)))
  const union = new Set([...setA, ...setB])
  return union.size > 0 ? intersection.size / union.size : 0
}

/**
 * Calculate similarity score between two tag arrays
 * Returns a score between 0 and 1
 */
export function calculateTagSimilarity(tagsA: string[], tagsB: string[]): number {
  if (tagsA.length === 0 || tagsB.length === 0) return 0
  
  const setA = new Set(tagsA.map(t => t.toLowerCase()))
  const setB = new Set(tagsB.map(t => t.toLowerCase()))
  
  return jaccardSimilarity(setA, setB)
}

/**
 * Smart matching result interface
 */
export interface SmartMatchResult {
  countries: string[]      // Recognized countries
  topics: string[]         // Recognized topics
  relatedTypes: string[]   // Recommended service types (now empty, kept for compatibility)
}

/**
 * Analyze article content and extract key matching information
 */
export function analyzeContent(
  title: string,
  excerpt: string = '',
  content: string = '',
  tags: string[] = []
): SmartMatchResult {
  // Combine all text for analysis
  const allText = `${title} ${excerpt} ${content} ${tags.join(' ')}`

  // Extract countries and topics
  const countries = extractCountries(allText)
  const topics = extractTopics(allText)

  // relatedTypes is now empty - services removed
  const relatedTypes: string[] = []

  return {
    countries,
    topics,
    relatedTypes
  }
}

/**
 * Find related articles based on content similarity
 */
export function findRelatedArticles(
  currentArticle: { id: string; title: string; excerpt: string; tags: string[] },
  allArticles: Array<{ id: string; title: string; excerpt: string; tags: string[] }>,
  limit: number = 3
): Array<{ id: string; title: string; similarity: number }> {
  const currentTags = new Set(currentArticle.tags.map(t => t.toLowerCase()))
  const currentTopics = new Set(extractTopics(`${currentArticle.title} ${currentArticle.excerpt}`))

  const scored = allArticles
    .filter(a => a.id !== currentArticle.id)
    .map(article => {
      const articleTags = new Set(article.tags.map(t => t.toLowerCase()))
      const articleTopics = new Set(extractTopics(`${article.title} ${article.excerpt}`))

      // Calculate similarity score
      const tagSimilarity = jaccardSimilarity(currentTags, articleTags)
      const topicSimilarity = jaccardSimilarity(currentTopics, articleTopics)

      // Weighted combination
      const score = tagSimilarity * 0.6 + topicSimilarity * 0.4

      return {
        id: article.id,
        title: article.title,
        similarity: score
      }
    })
    .filter(a => a.similarity > 0)
    .sort((a, b) => b.similarity - a.similarity)

  return scored.slice(0, limit)
}

/**
 * Get display name for a country code
 */
export function getCountryName(code: string): string {
  const names: Record<string, string> = {
    china: 'China',
    usa: 'United States',
    uk: 'United Kingdom',
    canada: 'Canada',
    australia: 'Australia',
    japan: 'Japan',
    singapore: 'Singapore',
    thailand: 'Thailand',
    malaysia: 'Malaysia',
    germany: 'Germany',
    france: 'France',
    switzerland: 'Switzerland'
  }
  return names[code.toLowerCase()] || code
}

/**
 * Get display name for a topic
 */
export function getTopicName(code: string): string {
  const names: Record<string, string> = {}
  return names[code.toLowerCase()] || code
}
