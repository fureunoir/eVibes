import gql from 'graphql-tag'

export const GET_CATEGORIES = gql`
  query getCategories {
    categories {
      edges {
        node {
          name
          uuid
          image
          description
          slug
        }
      }
    }
  }
`

export const GET_CATEGORY_BY_SLUG = gql`
  query getCategoryBySlug(
    $slug: String!
  ) {
    categories(
      slug: $slug
    ) {
      edges {
        node {
          name
          uuid
          image
          description
          slug
          filterableAttributes {
            possibleValues
            attributeName
          }
          minMaxPrices {
            maxPrice
            minPrice
          }
        }
      }
    }
  }
`