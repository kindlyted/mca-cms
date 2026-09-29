// i18n.config.ts - 仅配置 vueI18n 选项
// 翻译消息由 i18n/locales/*.json 提供，不要在此处定义 messages
export default defineI18nConfig(() => ({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en'
}))