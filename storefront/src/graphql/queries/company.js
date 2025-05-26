import gql from 'graphql-tag'

export const GET_COMPANY_INFO = gql`
  query getCompanyInfo {
    parameters {
      companyAddress
      companyName
      companyPhoneNumber
      emailFrom
      emailHostUser
      projectName
    }
  }
`