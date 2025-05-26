import gql from 'graphql-tag'

export const REGISTER = gql`
  mutation register(
      $firstName: String!, 
      $lastName: String!, 
      $email: String!,
      $phoneNumber: String!,
      $password: String!, 
      $confirmPassword: String!
  ) {
    createUser(
        firstName: $firstName, 
        lastName: $lastName,
        email: $email,
        phoneNumber: $phoneNumber,
        password: $password,
        confirmPassword: $confirmPassword
    ) {
      success
    }
  }
`

export const LOGIN = gql`
  mutation login(
      $email: String!, 
      $password: String!
  ) {
    obtainJwtToken(
        email: $email, 
        password: $password
    ) {
      accessToken
      refreshToken
      user {
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
    }
  }
`

export const REFRESH = gql`
  mutation refresh(
      $refreshToken: String!
  ) {
    refreshJwtToken(
        refreshToken: $refreshToken
    ) {
      accessToken
      refreshToken
      user {
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
    }
  }
`

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
      $firstName: String,
      $lastName: String,
      $email: String,
      $phoneNumber: String,
      $password: String,
      $confirmPassword: String,
  ) {
    updateUser(
        firstName: $firstName,
        lastName: $lastName,
        email: $email,
        phoneNumber: $phoneNumber,
        password: $password,
        confirmPassword: $confirmPassword,
    ) {
      user {
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
    }
  }
`

export const RESET_PASSWORD = gql`
  mutation resetPassword(
      $email: String!,
  ) {
    resetPassword(
        email: $email,
    ) {
      success
    }
  }
`

export const CONFIRM_RESET_PASSWORD = gql`
  mutation confirmResetPassword(
      $password: String!,
      $confirmPassword: String!,
      $token: String!,
      $uid: String!,
  ) {
    confirmResetPassword(
        password: $password,
        confirmPassword: $confirmPassword,
        token: $token,
        uid: $uid
    ) {
      success
    }
  }
`