import gql from 'graphql-tag'

export const CONTACT_US = gql`
  mutation contactUs(
      $email: String!, 
      $name: String!,
      $subject: String!,
      $message: String!,
  ) {
    contactUs(
        email: $email, 
        name: $name,
        subject: $subject,
        message: $message
    ) {
      error
      received
    }
  }
`