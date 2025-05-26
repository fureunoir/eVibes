export async function loadLocaleMessages(locale) {
  try {
    const messages = await import(`../locales/${locale}.json`)
    return messages.default || messages
  } catch (error) {
    console.error(`Не удалось загрузить локаль: ${locale}`, error)
    return {}
  }
}

export function getLocaleFilename(localeCode, localesConfig) {
  const localeInfo = localesConfig.find(locale => locale.code === localeCode)
  return localeInfo?.file || `${localeCode}.json`
}

export async function loadAllLocaleMessages(supportedLocales) {
  const messages = {}

  for (const locale of supportedLocales) {
    try {
      const localeMessages = await import(`../../locales/${locale.code}.json`)
      messages[locale.code] = localeMessages.default || localeMessages
    } catch (error) {
      console.error(`Не удалось загрузить локаль: ${locale.code}`, error)
      messages[locale.code] = {}
    }
  }

  return messages
}