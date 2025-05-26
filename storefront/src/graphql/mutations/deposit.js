import gql from 'graphql-tag'

export const DEPOSIT = gql`
  mutation deposit(
      $amount: Number!
  ) {
    contactUs(
        amount: $amount,
    ) {
      error
      received
    }
  }
`