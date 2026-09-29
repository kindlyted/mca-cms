export interface HowToStep {
  name: string
  text: string
  url?: string
  image?: string
}

export interface HowToSchemaOptions {
  name: string
  description?: string
  totalTime?: string
  steps?: HowToStep[]
}

interface HowToSchema {
  '@context': string
  '@type': 'HowTo'
  name: string
  description?: string
  totalTime?: string
  step: Array<{
    '@type': 'HowToStep'
    name: string
    text: string
    url?: string
    image?: string
  }>
}

/**
 * Default application steps for services
 */
const DEFAULT_STEPS: HowToStep[] = [
  {
    name: 'Submit Inquiry',
    text: 'Fill out the online inquiry form or contact us directly with your requirements.'
  },
  {
    name: 'Free Consultation',
    text: 'Our advisors review your request and provide a personalized proposal within 24-48 hours.'
  },
  {
    name: 'Proposal & Agreement',
    text: 'We match your needs with the right solution and confirm scope, timeline, and pricing.'
  },
  {
    name: 'Delivery & Coordination',
    text: 'Our team coordinates every step of the engagement and keeps you informed throughout.'
  },
  {
    name: 'Follow-Up & Support',
    text: 'We stay available after completion to support you with questions, updates, and adjustments.'
  }
]

/**
 * Generate HowTo Schema for service detail pages
 * Used to markup "Application Steps" so Google can display as rich snippet step list
 */
export function useHowToSchema(options: HowToSchemaOptions): HowToSchema | null {
  const steps = options.steps && options.steps.length > 0
    ? options.steps
    : DEFAULT_STEPS

  if (!steps || steps.length === 0) {
    return null
  }

  return {
    '@context': 'https://schema.org',
    '@type': 'HowTo',
    name: options.name,
    description: options.description || `Step-by-step guide on how to apply for ${options.name} through ${companyInfo.shortName}.`,
    totalTime: options.totalTime || 'P7D',
    step: steps.map((s, index) => ({
      '@type': 'HowToStep',
      position: index + 1,
      name: s.name,
      text: s.text,
      ...(s.url && { url: s.url }),
      ...(s.image && { image: s.image })
    }))
  }
}

// Default export
export default useHowToSchema
