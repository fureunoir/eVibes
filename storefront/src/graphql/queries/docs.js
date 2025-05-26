import gql from 'graphql-tag'

export const GET_DOCS = gql`
  query getDocs(
    $slug: String!
  ) {
    posts(
      slug: $slug
    ) {
      edges {
        node {
          content
        }
      }
    }
  }
`