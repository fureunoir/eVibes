import gql from 'graphql-tag'

export const LANGUAGES_FRAGMENT = gql`
  fragment Languages on LanguageType {
    code
    flag
    name
  }
`