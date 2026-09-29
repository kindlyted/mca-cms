interface AuthorInfo {
  id: string
  name: string
  role: string
  url?: string
}

interface BaseMeta {
  id: string
  status: 'published' | 'draft' | 'archived'
  author?: AuthorInfo
  featured?: boolean
  priority: number
  createdAt: string
  updatedAt: string
}

interface SeoData {
  title: string
  description: string
  keywords: string
  og?: {
    title: string
    description: string
    image: string
    url?: string
    type?: 'website' | 'article'
  }
  twitter?: {
    card: 'summary' | 'summary_large_image'
    title: string
    description: string
    image?: string
  }
  canonical?: string
}

interface MediaAsset {
  url: string
  alt: string
  caption?: string
}

interface Visuals {
  cover: MediaAsset
  thumbnail?: MediaAsset
  gallery?: MediaAsset[]
}

interface Overview {
  title: string
  subtitle?: string
  excerpt: string
}

interface Reference {
  title: string
  url: string
  author?: string
  organization?: string
}

interface ContentMetadata {
  publishedAt: string
  updatedAt: string
  source?: string
  sourceUrl?: string
  references?: Reference[]
  relatedServices?: string[]
  relatedPartners?: string[]
  relatedArticles?: string[]
}

interface Tag {
  id: string
  name: string
  slug: string
  group: string
}

interface CtaConfig {
  enabled: boolean
  text?: string
  link?: string
  primary?: { text: string; link: string; type?: string }
  secondary?: { text: string; link: string; type?: string }
  banner?: { text?: string; backgroundColor?: string; textColor?: string }
}

interface FaqItem {
  question: string
  answer: string
}

export type {
  AuthorInfo,
  BaseMeta,
  SeoData,
  MediaAsset,
  Visuals,
  Overview,
  Reference,
  ContentMetadata,
  Tag,
  CtaConfig,
  FaqItem
}
