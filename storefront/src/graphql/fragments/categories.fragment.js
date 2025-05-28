import gql from 'graphql-tag'

export const CATEGORY_FRAGMENT = gql`
  fragment Category on CategoryType {
    name
    uuid
    image
    description
    slug
  }
`