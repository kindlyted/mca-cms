import { companyInfo } from '~/utils/config'

export type PageType = 'home' | 'about' | 'contact' | 'service' | 'partner' | 'blog' | 'product' | 'minimal'

interface OrganizationSchema {
  '@context': string
  '@type': 'Organization'
  name: string
  alternateName?: string
  url?: string
  logo?: {
    '@type': 'ImageObject'
    url: string
  }
  description?: string
  address?: {
    '@type': 'PostalAddress'
    streetAddress: string
    addressLocality: string
    addressRegion: string
    addressCountry: string
  }
  contactPoint?: {
    '@type': 'ContactPoint'
    telephone: string
    email: string
    contactType: string
    availableLanguage: string[]
  }
  openingHours?: string
  sameAs?: string[]
  parentOrganization?: {
    '@type': 'Organization'
    name: string
    description?: string
  }
}

/**
 * Unified Organization Schema entry point
 * All schemas use companyInfo.shortName as the primary name (对外品牌)
 * with companyInfo.name as alternateName (母公司).
 * Homepage and about page additionally include parentOrganization.
 *
 * @param pageType Page type
 * @returns Organization Schema for the corresponding type
 */
export function useOrganizationSchema(pageType: PageType): OrganizationSchema {
  const config = useRuntimeConfig()
  const baseUrl = config.public.siteUrl || companyInfo.siteUrl
  const logoUrl = `${baseUrl}/logo.png`

  const baseOrg = {
    '@context': 'https://schema.org',
    '@type': 'Organization' as const,
    name: companyInfo.shortName,
    alternateName: companyInfo.name,
    url: baseUrl,
  }

  const serviceOrg: OrganizationSchema = {
    ...baseOrg,
    description: companyInfo.description,
  }

  const contactOrg: OrganizationSchema = {
    ...serviceOrg,
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: companyInfo.phone,
      email: companyInfo.email,
      contactType: 'customer service',
      availableLanguage: ['Chinese', 'English']
    },
    openingHours: companyInfo.workingHours
  }

  const parentOrg = {
    '@type': 'Organization' as const,
    name: companyInfo.name,
    description: 'Parent company operating multiple healthcare projects'
  }

  const fullOrg: OrganizationSchema = {
    ...contactOrg,
    logo: {
      '@type': 'ImageObject',
      url: logoUrl
    },
    address: {
      '@type': 'PostalAddress',
      streetAddress: companyInfo.address,
      addressLocality: 'Hong Kong',
      addressRegion: 'Hong Kong',
      addressCountry: 'HK'
    },
    sameAs: [
      companyInfo.socialLinks.facebook,
      companyInfo.socialLinks.twitter,
      companyInfo.socialLinks.linkedin
    ].filter(Boolean),
    parentOrganization: parentOrg
  }

  switch (pageType) {
    case 'home':
      return fullOrg
    case 'about':
      return fullOrg
    case 'contact':
      return contactOrg
    case 'service':
      return serviceOrg
    case 'partner':
      return serviceOrg
    case 'product':
      return serviceOrg
    case 'blog':
      return {
        ...serviceOrg,
        logo: {
          '@type': 'ImageObject',
          url: logoUrl
        }
      }
    case 'minimal':
      return baseOrg
    default:
      return baseOrg
  }
}

// Default export
export default useOrganizationSchema
