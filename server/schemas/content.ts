import { z } from 'zod'

export const authorSchema = z.object({
  id: z.string().min(1, 'Author ID is required'),
  name: z.string().min(1, 'Author name is required'),
  role: z.string(),
  url: z.string().url().optional()
})

export const seoSchema = z.object({
  title: z.string().min(1, 'SEO title is required'),
  description: z.string().min(1, 'SEO description is required'),
  keywords: z.union([
    z.array(z.string()),
    z.string()
  ]).transform(val => typeof val === 'string' ? val.split(',').map(k => k.trim()) : val),
  og: z.object({
    title: z.string(),
    description: z.string(),
    image: z.string(),
    url: z.string(),
    type: z.enum(['website', 'article']).default('website')
  }).optional(),
  twitter: z.object({
    card: z.enum(['summary', 'summary_large_image']).default('summary_large_image'),
    title: z.string(),
    description: z.string(),
    image: z.string()
  }).optional(),
  canonical: z.string().optional(),
  hreflang: z.array(z.object({
    lang: z.string(),
    url: z.string()
  })).optional()
})

export const seoStrictSchema = z.object({
  title: z.string().min(1, 'SEO title is required'),
  description: z.string().min(1, 'SEO description is required'),
  keywords: z.union([
    z.array(z.string()),
    z.string()
  ]).transform(val => typeof val === 'string' ? val.split(',').map(k => k.trim()) : val)
})

export const visualsSchema = z.object({
  cover: z.object({
    url: z.string(),
    alt: z.string().default(''),
    caption: z.string().optional()
  }),
  thumbnail: z.object({
    url: z.string(),
    alt: z.string().default('')
  }).optional(),
  gallery: z.array(z.object({
    url: z.string(),
    alt: z.string().default('')
  })).default([])
}).optional()

export const overviewSchema = z.object({
  title: z.string().min(1, 'Overview title is required'),
  excerpt: z.string().min(1, 'Overview excerpt is required'),
  summary: z.string().optional(),
  subtitle: z.string().optional(),
  description: z.string().optional()
})

export const contentMetaSchema = z.object({
  publishedAt: z.string().optional(),
  updatedAt: z.string().optional(),
  source: z.string().optional(),
  references: z.array(z.object({
    title: z.string(),
    url: z.string().optional()
  })).default([]),
  relatedPartners: z.array(z.string()).default([])
})

export const bodySchema = z.object({
  format: z.enum(['markdown', 'html', 'richtext']).default('markdown'),
  content: z.string().min(1, 'Body content is required')
})

export const ctaSchema = z.object({
  enabled: z.boolean().default(true),
  text: z.string().min(1),
  link: z.string().min(1)
})

export const faqItemSchema = z.object({
  question: z.string().min(1, 'FAQ question is required'),
  answer: z.string().min(1, 'FAQ answer is required')
})

export const faqItemShortSchema = z.object({
  q: z.string().min(1, 'FAQ q is required'),
  a: z.string().min(1, 'FAQ a is required')
})

export const processStepSchema = z.object({
  title: z.string(),
  description: z.string(),
  duration: z.string().optional(),
  cost: z.string().optional()
})

export const processSchema = z.object({
  title: z.string().optional(),
  steps: z.array(processStepSchema)
})

export const conditionItemSchema = z.object({
  key: z.string(),
  value: z.string()
})

export const conditionsSchema = z.object({
  title: z.string().optional(),
  items: z.array(conditionItemSchema)
})

export const geoSchema = z.object({
  citationSources: z.array(z.string()).default([]),
  keyFacts: z.array(z.string()).default([]),
  definitiveClaims: z.array(z.string()).default([])
})

export const tagSchema = z.object({
  id: z.string(),
  name: z.string(),
  slug: z.string(),
  group: z.string()
})

const baseEntitySchema = z.object({
  _type: z.string(),
  meta: z.object({
    id: z.string().min(1, 'Entity ID is required'),
    category: z.string().optional(),
    region: z.string().optional(),
    country: z.string().optional(),
    language: z.string().optional(),
    status: z.enum(['draft', 'published', 'archived']),
    author: authorSchema.optional(),
    slug: z.string().optional(),
    featured: z.boolean().default(false),
    pinned: z.boolean().default(false),
    priority: z.number().int().default(0),
    readTime: z.number().int().nonnegative().optional(),
    createdAt: z.string().min(1),
    updatedAt: z.string().min(1),
    lastReviewed: z.string().optional(),
    reviewedBy: authorSchema.optional()
  }),
  seo: seoSchema.optional(),
  visuals: visualsSchema,
  overview: overviewSchema,
  content: contentMetaSchema.optional(),
  body: z.union([
    bodySchema,
    z.object({
      format: z.string(),
      content: z.any()
    }),
    z.string()
  ]).optional(),
  faq: z.union([
    z.array(faqItemSchema),
    z.array(faqItemShortSchema),
    z.array(z.object({
      question: z.any(),
      answer: z.any()
    }))
  ]).optional(),
  cta: ctaSchema.optional()
})

export const inclusionSchema = z.object({
  icon: z.string(),
  label: z.string()
})

export const pricingTierSchema = z.object({
  name: z.string(),
  price: z.number(),
  unit: z.string(),
  description: z.string(),
  inclusions: z.array(inclusionSchema).default([])
})

export const testimonialSchema = z.object({
  name: z.string(),
  country: z.string(),
  quote: z.string(),
  rating: z.number().min(1).max(5).default(5)
})

export const pricingSchema = z.object({
  currency: z.string().default('USD'),
  tiers: z.array(pricingTierSchema).default([]),
  inclusions: z.array(inclusionSchema).default([]),
  exclusions: z.array(z.string()).default([]),
    exampleTotal: z.object({
      description: z.string().optional(),
      amount: z.number().optional()
    }).optional()
})

export const serviceSchema = baseEntitySchema.extend({
  _type: z.literal('service'),
  meta: baseEntitySchema.shape.meta.extend({
    category: z.string().optional(),
    difficulty: z.string().optional(),
    duration: z.string().optional(),
    priceRange: z.string().optional()
  }),
  cover: z.object({
    url: z.string(),
    alt: z.string().default('')
  }).optional(),
  description: z.string().default(''),
  introduction: z.string().default(''),
  procedure: z.string().default(''),
  outcome: z.string().default(''),
  comparison: z.string().default('').optional(),
  pricing: pricingSchema.optional(),
  testimonials: z.array(testimonialSchema).default([]),
  highlights: z.union([
    z.array(z.object({
      label: z.string(),
      value: z.string()
    })),
    z.array(z.string())
  ]).optional(),
  process: processSchema.optional(),
  conditions: conditionsSchema.optional(),
  references: z.array(z.object({
    title: z.string(),
    url: z.string().optional()
  })).optional(),
  relatedPartners: z.array(z.string()).optional(),
  tags: z.object({
    primary: z.array(tagSchema).optional(),
    secondary: z.array(tagSchema).optional()
  }).optional(),
  geo: geoSchema.optional()
})

export const partnerSchema = baseEntitySchema.extend({
  _type: z.literal('partner'),
  meta: baseEntitySchema.shape.meta.extend({
    category: z.literal('partner').optional(),
    type: z.string(),
    city: z.string().optional(),
    region: z.string().optional(),
    country: z.string().default('China')
  }),
  cover: z.object({
    url: z.string(),
    alt: z.string().default('')
  }).optional(),
  description: z.string().optional(),
  highlights: z.array(z.string()).default([]),
  institution: z.object({
    name: z.string(),
    established: z.number().int().positive(),
    certifications: z.array(z.string()),
    ranking: z.string().optional(),
    languages: z.array(z.string()),
    address: z.object({
      street: z.string(),
      city: z.string(),
      province: z.string(),
      postalCode: z.string(),
      country: z.string().optional()
    }),
    geo: z.object({
      latitude: z.string(),
      longitude: z.string()
    }).optional(),
    contact: z.object({
      phone: z.string(),
      email: z.string().optional(),
      website: z.string().optional(),
      workingHours: z.string()
    }),
    rating: z.object({
      value: z.number().min(0).max(5),
      count: z.number().int().nonnegative().optional()
    })
  }).optional(),
  team: z.array(z.object({
    name: z.string(),
    title: z.string(),
    qualifications: z.string(),
    languages: z.array(z.string()).optional(),
    specialties: z.array(z.string()),
    image: z.string().optional()
  })).optional(),
  relatedServices: z.array(z.string()).optional(),
  cta: ctaSchema.optional(),
  stats: z.object({
    clients: z.string().optional(),
    team: z.string().optional(),
    locations: z.number().optional(),
    rating: z.string().optional()
  }).optional(),
  services: z.array(z.string()).optional(),
  references: z.array(z.object({
    title: z.string(),
    url: z.string().optional()
  })).optional()
})

export const productSchema = baseEntitySchema.extend({
  _type: z.literal('product'),
  meta: baseEntitySchema.shape.meta.extend({
    category: z.string().optional(),
    difficulty: z.string().optional(),
    duration: z.string().optional(),
    priceRange: z.string().optional()
  }),
  // ---- 商品扩展字段（站内成交，由 contentgen 生成）----
  price: z.number().optional(),
  compareAtPrice: z.number().optional(),
  colors: z.array(z.string()).optional(),
  sizes: z.array(z.object({
    label: z.string(),
    price: z.number(),
    compareAtPrice: z.number().optional()
  })).optional(),
  dimensions: z.string().optional(),
  thickness: z.string().optional(),
  currency: z.string().optional(),
  inStock: z.boolean().optional().default(true),
  // ---------------------------------------------------
  cover: z.object({
    url: z.string(),
    alt: z.string().default('')
  }).optional(),
  description: z.string().default(''),
  introduction: z.string().default(''),
  procedure: z.string().default(''),
  outcome: z.string().default(''),
  comparison: z.string().default('').optional(),
  pricing: pricingSchema.optional(),
  testimonials: z.array(testimonialSchema).default([]),
  highlights: z.union([
    z.array(z.object({
      label: z.string(),
      value: z.string()
    })),
    z.array(z.string())
  ]).optional(),
  process: processSchema.optional(),
  conditions: conditionsSchema.optional(),
  references: z.array(z.object({
    title: z.string(),
    url: z.string().optional()
  })).optional(),
  relatedPartners: z.array(z.string()).optional(),
  tags: z.object({
    primary: z.array(tagSchema).optional(),
    secondary: z.array(tagSchema).optional()
  }).optional(),
  geo: geoSchema.optional()
})

export const blogSchema = baseEntitySchema.extend({
  _type: z.literal('blog'),
  meta: baseEntitySchema.shape.meta.extend({
    country: z.string().optional()
  }),
  cover: z.object({
    url: z.string(),
    alt: z.string().default(''),
    caption: z.string().optional()
  }).optional(),
  tags: z.object({
    primary: z.array(tagSchema).optional(),
    secondary: z.array(tagSchema).optional()
  }).optional(),
  references: z.array(z.object({
    title: z.string(),
    url: z.string().optional()
  })).optional(),
  source: z.string().optional(),
  sourceUrl: z.string().optional(),
  relatedPartners: z.array(z.string()).optional(),
  relatedServices: z.array(z.string()).optional(),
  engagement: z.object({
    views: z.number().int().nonnegative().default(0),
    likes: z.number().int().nonnegative().default(0),
    shares: z.number().int().nonnegative().default(0),
    comments: z.number().int().nonnegative().default(0)
  }).optional()
})

export type ServiceType = z.infer<typeof serviceSchema>
export type PartnerType = z.infer<typeof partnerSchema>
export type BlogType = z.infer<typeof blogSchema>
export type ProductType = z.infer<typeof productSchema>

export function validateService(data: unknown): ServiceType | null {
  const result = serviceSchema.safeParse(data)
  if (!result.success) {
    console.error('❌ Service validation failed:', result.error.issues)
    return null
  }
  return result.data
}

export function validateProvider(data: unknown): PartnerType | null {
  const result = partnerSchema.safeParse(data)
  if (!result.success) {
    console.error('❌ Provider validation failed:', result.error.issues)
    return null
  }
  return result.data
}

export function validateBlog(data: unknown): BlogType | null {
  const result = blogSchema.safeParse(data)
  if (!result.success) {
    console.error('❌ Blog validation failed:', result.error.issues)
    return null
  }
  return result.data
}

export function validateProduct(data: unknown): ProductType | null {
  const result = productSchema.safeParse(data)
  if (!result.success) {
    console.error('❌ Product validation failed:', result.error.issues)
    return null
  }
  return result.data
}
