import gql from 'graphql-tag'

export const COMPANY_FRAGMENT = gql`
  fragment Company on ConfigType {
    companyAddress
    companyName
    companyPhoneNumber
    emailFrom
    emailHostUser
    projectName
  }
`