import gql from 'graphql-tag'

export const ACTIVATE_USER = gql`
  mutation activateUser(
      $token: String!,
      $uid: String!
  ) {
    activateUser(
        token: $token,
        uid: $uid
    ) {
      success
    }
  }
`

export const UPDATE_USER = gql`
  mutation updateUser(
      $uuid: UUID!,
      $firstName: String,
      $lastName: String,
      $email: String,
      $phoneNumber: String,
      $password: String,
      $confirmPassword: String,
  ) {
    updateUser(
        uuid: $uuid,
        firstName: $firstName,
        lastName: $lastName,
        email: $email,
        phoneNumber: $phoneNumber,
        password: $password,
        confirmPassword: $confirmPassword,
    ) {
      user {
        ...User
      }
    }
  }
`