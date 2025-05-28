import gql from 'graphql-tag'

export const GET_POSTS = gql`
  query getPosts {
    posts {
      edges {
        node {
          content
        }
      }
    }
  }
`

export const GET_POST_BY_SLUG = gql`
  query getPostBySlug(
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