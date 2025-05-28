import gql from "graphql-tag";

export const SWITCH_LANGUAGE = gql`
  mutation setlanguage(
      $uuid: UUID!,
      $language: String,
  ) {
    updateUser(
        uuid: $uuid,
        language: $language
    ) {
      user {
        ...User
      }
    }
  }
`