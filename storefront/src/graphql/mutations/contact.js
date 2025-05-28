import gql from 'graphql-tag'

export const CONTACT_US = gql`
  mutation contactUs(
      $name: String!,
      $email: String!,
      $phoneNumber: String,
      $subject: String!,
      $message: String!,
  ) {
    contactUs(
        name: $name,
        email: $email, 
        phoneNumber: $phoneNumber,
        subject: $subject,
        message: $message
    ) {
      error
      received
    }
  }
`