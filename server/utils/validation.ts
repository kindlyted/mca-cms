import { validateService, validateProvider, validateBlog, validateProduct } from '../schemas/content'
import type { ServiceType, PartnerType, BlogType, ProductType } from '../schemas/content'

export function validateEntity(entityType: string, data: unknown): ServiceType | PartnerType | BlogType | ProductType | null {
  switch (entityType) {
    case 'service':
      return validateService(data)
    case 'partner':
      return validateProvider(data)
    case 'blog':
      return validateBlog(data)
    case 'product':
      return validateProduct(data)
    default:
      console.error(`❌ Unknown entity type for validation: ${entityType}`)
      return null
  }
}

export function logValidationErrors(entityType: string, id: string, errors: any[]) {
  if (process.env.NODE_ENV === 'development') {
    console.group(`🔍 Validation Error: ${entityType}/${id}`)
    errors.forEach((error, index) => {
      console.error(`${index + 1}. ${error.path.join('.')}: ${error.message}`)
    })
    console.groupEnd()
  }
}
