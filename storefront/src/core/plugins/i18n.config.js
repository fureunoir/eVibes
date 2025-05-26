import { createI18n } from 'vue-i18n'
import {DEFAULT_LOCALE, LOCALE_STORAGE_LOCALE_KEY, SUPPORTED_LOCALES} from "@/config/index.js";
import {loadAllLocaleMessages} from "@/core/helpers/i18n-utils.js";

const savedLocale = localStorage.getItem(LOCALE_STORAGE_LOCALE_KEY)
const currentLocale = savedLocale && SUPPORTED_LOCALES.some(locale => locale.code === savedLocale)
  ? savedLocale
  : DEFAULT_LOCALE

if (!savedLocale) {
  localStorage.setItem(LOCALE_STORAGE_LOCALE_KEY, DEFAULT_LOCALE)
}

const i18n = createI18n({
  locale: currentLocale,
  fallbackLocale: DEFAULT_LOCALE,
  allowComposition: true,
  legacy: false,
  globalInjection: true,
  messages: {}
})

export async function setupI18n() {
  const messages = await loadAllLocaleMessages(SUPPORTED_LOCALES)

  Object.keys(messages).forEach(locale => {
    i18n.global.setLocaleMessage(locale, messages[locale])
  })

  return i18n
}

export default i18n
