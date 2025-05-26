import i18n from '@/core/plugins/i18n.config'

const isEmail = (email) => {
  if (!email) return required(email);
  if (/.+@.+\..+/.test(email)) return true
  const { t } = i18n.global
  return t('errors.mail')
}

const required = (text) => {
  if (text) return true
  const { t } = i18n.global
  return t('errors.required')
}

const isPasswordValid = (pass) => {
  const { t } = i18n.global

  if (pass.length < 8) {
    return t('errors.needMin')
  }

  if (!/[a-z]/.test(pass)) {
    return t('errors.needLower')
  }

  if (!/[A-Z]/.test(pass)) {
    return t('errors.needUpper')
  }

  if (!/\d/.test(pass)) {
    return t('errors.needNumber')
  }

  if (!/[#.?!@$%^&*'()_+=:;"'/>.<,|\-]/.test(pass)) {
    return t('errors.needSpecial')
  }

  return true
}

export { required, isEmail, isPasswordValid }