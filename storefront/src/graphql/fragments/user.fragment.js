import gql from 'graphql-tag'

export const USER_FRAGMENT = gql`
  fragment User on UserType {
    avatar
    uuid
    attributes
    language
    email
    firstName
    lastName
    phoneNumber
    balance {
      amount
    }
  }
`