// APP

export const APP_NAME = import.meta.env.EVIBES_PROJECT_NAME

export const APP_NAME_KEY = APP_NAME.toLowerCase()



// LOCALES

export const SUPPORTED_LOCALES = [
  {
    code: 'en-gb',
    default: true
  }
]

export const DEFAULT_LOCALE = SUPPORTED_LOCALES.find(locale => locale.default)?.code || 'en-gb'



// LOCAL STORAGE

export const LOCALE_STORAGE_LOCALE_KEY = `${APP_NAME_KEY}-user-locale`;

export const LOCALE_STORAGE_REFRESH_KEY = `${APP_NAME_KEY}-refresh`;

export const LOCALE_STORAGE_STAY_LOGIN_KEY = `${APP_NAME_KEY}-remember`;