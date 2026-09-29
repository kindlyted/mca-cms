// Company information configuration — single source of truth
// Replace the placeholder values below with your own company/brand info.
export const companyInfo = {
  name: 'Your Company',
  shortName: 'YourBrand',
  address: 'Your street address, City, Country',
  phone: '+00 0000-0000',
  email: 'info@yourdomain.com',
  workingHours: 'Monday to Friday: 9:00 - 18:00',
  copyright: 'All Rights Reserved',
  year: '2026',

  // Site URL (can be overridden by NUXT_PUBLIC_SITE_URL env var in nuxt.config.ts)
  siteUrl: 'https://www.yourdomain.com',

  // Brand description (used in Schema, meta, etc.)
  description: 'Your company delivers professional services and tailored solutions to clients worldwide. Contact us to discuss how we can help you achieve your goals.',

  // Logo path (relative to public/)
  logoPath: '/images/logo/logo.png',

  // External / friendly links (displayed in footer)
  externalLinks: [
    { name: 'Example Partner', url: 'https://example.com' },
    { name: 'Industry Association', url: 'https://example.com' },
    { name: 'Case Studies', url: 'https://example.com' }
  ],

  // About page — structural data with i18n key references
  // Values (numbers, icons, initials) are company-specific; text comes from i18n via *Key fields
  aboutPage: {
    statistics: [
      { value: '15+', labelKey: 'pages.about.stats.years' },
      { value: '500+', labelKey: 'pages.about.stats.projects' },
      { value: '98%', labelKey: 'pages.about.stats.satisfaction' },
      { value: '120+', labelKey: 'pages.about.stats.clients' }
    ],
    coreValues: [
      { icon: '🎯', titleKey: 'pages.about.values.quality.title', descriptionKey: 'pages.about.values.quality.description' },
      { icon: '🤝', titleKey: 'pages.about.values.trust.title', descriptionKey: 'pages.about.values.trust.description' },
      { icon: '💡', titleKey: 'pages.about.values.transparency.title', descriptionKey: 'pages.about.values.transparency.description' }
    ],
    teamMembers: [
      { initials: 'ME', nameKey: 'pages.about.team.members.editorial.name', roleKey: 'pages.about.team.members.editorial.role', bioKey: 'pages.about.team.members.editorial.bio' },
      { initials: 'MT', nameKey: 'pages.about.team.members.leadership.name', roleKey: 'pages.about.team.members.leadership.role', bioKey: 'pages.about.team.members.leadership.bio' },
      { initials: 'CS', nameKey: 'pages.about.team.members.support.name', roleKey: 'pages.about.team.members.support.role', bioKey: 'pages.about.team.members.support.bio' }
    ],
    reasons: [
      { titleKey: 'pages.about.whyChooseUs.expertise.title', descriptionKey: 'pages.about.whyChooseUs.expertise.description' },
      { titleKey: 'pages.about.whyChooseUs.network.title', descriptionKey: 'pages.about.whyChooseUs.network.description' },
      { titleKey: 'pages.about.whyChooseUs.support.title', descriptionKey: 'pages.about.whyChooseUs.support.description' },
      { titleKey: 'pages.about.whyChooseUs.savings.title', descriptionKey: 'pages.about.whyChooseUs.savings.description' }
    ]
  },

  // Social media links
  socialLinks: {
    facebook: 'https://www.facebook.com/yourbrand',
    twitter: 'https://twitter.com/yourbrand',
    linkedin: 'https://www.linkedin.com/company/yourbrand'
  }
}