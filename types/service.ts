import type { BaseMeta, Overview, FaqItem } from './content'

interface ServiceMeta extends BaseMeta {
  difficulty: string
  duration: string
  priceRange: string
}

interface PricingTier {
  name: string
  price: number
  unit: string
  description: string
}

interface Pricing {
  currency: string
  tiers: PricingTier[]
  inclusions?: Inclusion[]
  exclusions: string[]
  exampleTotal?: {
    description?: string
    amount?: number
  }
}

interface Inclusion {
  icon: string
  label: string
}

interface Testimonial {
  name: string
  country?: string
  quote: string
  rating?: number
}

interface ServiceEntity {
  _type: 'service'
  meta: ServiceMeta
  seo: {
    title: string
    description: string
    keywords: string
  }
  cover: {
    url: string
    alt: string
  }
  overview: {
    title: string
    excerpt: string
    subtitle?: string
  }
  description?: string
  pricing?: Pricing
  testimonials?: Testimonial[]
  faq?: FaqItem[]
  highlights?: string[]
  conditions?: {
    title?: string
    items: Array<{ key: string; value: string }>
  }
  process?: {
    title?: string
    steps: Array<{
      title: string
      description: string
      duration?: string
      cost?: string
    }>
  }
  references?: Array<{
    title: string
    url?: string
  }>
  relatedPartners?: string[]
}

export type {
  ServiceMeta,
  ServiceEntity
}
