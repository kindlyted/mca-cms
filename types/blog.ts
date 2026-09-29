interface BlogEntity {
  _type: 'blog'
  meta: {
    id: string
    slug?: string
    language: string
    status: string
    region?: string
    country?: string
    readTime?: number
    featured?: boolean
    priority?: number
    createdAt: string
    updatedAt: string
  }
  seo: {
    title: string
    description: string
    keywords: string
  }
  cover: {
    url: string
    alt: string
    caption?: string
  }
  overview: {
    title: string
    subtitle?: string
    excerpt: string
  }
  body: string | {
    format: string
    content?: string
    sections?: Array<{
      type: string
      level?: number
      text?: string
      items?: string[] | Array<Record<string, string>>
      src?: string
      alt?: string
      headers?: string[]
      rows?: string[][]
      caption?: string
      style?: string
    }>
  }
  faq?: Array<{ q: string; a: string }>
  tags?: {
    primary?: Array<{ id: string; name: string; slug: string; group: string }>
    secondary?: Array<{ id: string; name: string; slug: string; group: string }>
  }
  references?: Array<{ title: string; url?: string }>
  source?: string
  sourceUrl?: string
  relatedPartners?: string[]
  relatedServices?: string[]
  cta?: Record<string, unknown>
}

export type { BlogEntity }
