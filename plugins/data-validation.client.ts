export default defineNuxtPlugin(() => {
  if (process.env.NODE_ENV === 'development') {
    console.log('%c🔍 Data Validation Enabled', 'color: #10B981; font-size: 16px; font-weight: bold;')
    console.log('%cAll API responses are validated with Zod schemas', 'color: #6B7280; font-size: 12px;')
    console.log('%cCheck server logs for validation errors', 'color: #F59E0B; font-size: 12px;')
  }
})
