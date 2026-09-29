import type { BaseMeta } from './content'

interface PartnerMeta extends BaseMeta {
  type: string
  city: string
  region: string
  country: string
}

interface InstitutionInfo {
  name: string
  established: number
  certifications: string[]
  ranking?: string
  languages: string[]
  address: {
    street: string
    city: string
    province: string
    postalCode: string
  }
  geo: {
    latitude: string
    longitude: string
  }
  contact: {
    phone: string
    email?: string
    website?: string
    workingHours: string
  }
  rating: {
    value: number
    count: number
  }
}

interface TeamMember {
  name: string
  title: string
  qualifications: string
  specialties: string[]
}

interface PartnerEntity {
  _type: 'partner'
  meta: PartnerMeta
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
  institution: InstitutionInfo
  description?: string
  services?: string[]
  team?: TeamMember[]
  relatedServices?: string[]
  faq?: { q: string; a: string }[]
  cta?: {
    enabled: boolean
    text: string
    link: string
  }
}

export type {
  PartnerMeta,
  InstitutionInfo,
  TeamMember,
  PartnerEntity
}
