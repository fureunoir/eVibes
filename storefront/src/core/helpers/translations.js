import i18n from '@/core/plugins/i18n.config';
import {DEFAULT_LOCALE, LOCALE_STORAGE_LOCALE_KEY, SUPPORTED_LOCALES} from "@/config/index.js";

const translation = {
  get currentLocale() {
    return i18n.global.locale.value
  },

  set currentLocale(newLocale) {
    i18n.global.locale.value = newLocale
  },

  switchLanguage(newLocale) {
    translation.currentLocale = newLocale

    document.querySelector('html').setAttribute('lang', newLocale)

    localStorage.setItem(LOCALE_STORAGE_LOCALE_KEY, newLocale)
  },

  isLocaleSupported(locale) {
    if (locale) {
      return SUPPORTED_LOCALES.some(supportedLocale => supportedLocale.code === locale);
    }
    return false
  },

  getUserLocale() {
    const locale =
      window.navigator.language ||
      DEFAULT_LOCALE.code

    return {
      locale: locale,
      localeNoRegion: locale.split('-')[0]
    }
  },

  getPersistedLocale() {
    const persistedLocale = localStorage.getItem(LOCALE_STORAGE_LOCALE_KEY)

    if (translation.isLocaleSupported(persistedLocale)) {
      return persistedLocale
    } else {
      return null
    }
  },

  guessDefaultLocale() {
    const userPersistedLocale = translation.getPersistedLocale()
    if (userPersistedLocale) {
      return userPersistedLocale
    }

    const userPreferredLocale = translation.getUserLocale()

    if (translation.isLocaleSupported(userPreferredLocale.locale)) {
      return userPreferredLocale.locale
    }

    if (translation.isLocaleSupported(userPreferredLocale.localeNoRegion)) {
      return userPreferredLocale.localeNoRegion
    }

    return DEFAULT_LOCALE.code
  },

  async routeMiddleware(to, _from, next) {
    const paramLocale = to.params.locale

    if (!translation.isLocaleSupported(paramLocale)) {
      return next(translation.guessDefaultLocale())
    }

    await translation.switchLanguage(paramLocale)

    return next()
  },

  i18nRoute(to) {
    return {
      ...to,
      params: {
        locale: translation.currentLocale,
        ...to.params
      }
    }
  }
}

export default translation
