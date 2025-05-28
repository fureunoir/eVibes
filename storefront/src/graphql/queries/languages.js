import gql from 'graphql-tag'
import {LANGUAGES_FRAGMENT} from "@/graphql/fragments/languages.fragment.js";

export const GET_LANGUAGES = gql`
  query getLanguages {
    languages {
      ...Languages
    }
  }
  ${LANGUAGES_FRAGMENT}
`