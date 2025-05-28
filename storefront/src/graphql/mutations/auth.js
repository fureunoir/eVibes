import gql from 'graphql-tag'
import {USER_FRAGMENT} from "@/graphql/fragments/user.fragment.js";

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
        ...User
      }
    }
  }
  ${USER_FRAGMENT}
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
        ...User
      }
    }
  }
  ${USER_FRAGMENT}
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

export const NEW_PASSWORD = gql`
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