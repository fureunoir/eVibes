import i18n from '@/core/plugins/i18n.config';
import {DEFAULT_LOCALE, LOCALE_STORAGE_LOCALE_KEY, SUPPORTED_LOCALES} from "@/config/index.js";

const translations = {
  get currentLocale() {
    return i18n.global.locale.value
  },

  set currentLocale(newLocale) {
    i18n.global.locale.value = newLocale
  },

  switchLanguage(newLocale, router = null, route = null) {
    translations.currentLocale = newLocale

    document.querySelector('html').setAttribute('lang', newLocale)

    localStorage.setItem(LOCALE_STORAGE_LOCALE_KEY, newLocale)

    if (router && route) {
      const newRoute = {
        ...route,
        params: {
          ...route.params,
          locale: newLocale
        }
      };

      router.push(newRoute).catch(err => {
        if (err.name !== 'NavigationDuplicated') {
          console.error('Navigation error:', err);
        }
      });
    }
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

    if (translations.isLocaleSupported(persistedLocale)) {
      return persistedLocale
    } else {
      return null
    }
  },

  guessDefaultLocale() {
    const userPersistedLocale = translations.getPersistedLocale()
    if (userPersistedLocale) {
      return userPersistedLocale
    }

    const userPreferredLocale = translations.getUserLocale()

    if (translations.isLocaleSupported(userPreferredLocale.locale)) {
      return userPreferredLocale.locale
    }

    if (translations.isLocaleSupported(userPreferredLocale.localeNoRegion)) {
      return userPreferredLocale.localeNoRegion
    }

    return DEFAULT_LOCALE.code
  },

  async routeMiddleware(to, _from, next) {
    const paramLocale = to.params.locale

    if (!translations.isLocaleSupported(paramLocale)) {
      return next(translations.guessDefaultLocale())
    }

    await translations.switchLanguage(paramLocale)

    return next()
  },

  i18nRoute(to) {
    return {
      ...to,
      params: {
        locale: translations.currentLocale,
        ...to.params
      }
    }
  }
}

export default translations
