import gql from 'graphql-tag'

export const GET_PRODUCTS = gql`
  query getProducts(
    $after: String,
    $first: Number,
    $categorySlugs: String,
    $orderBy: String,
    $minPrice: String,
    $maxPrice: String,
    $name: String
  ) {
    products(
      after: $after,
      first: $first,
      categorySlugs: $categorySlugs,
      orderBy: $orderBy,
      minPrice: $minPrice,
      maxPrice: $maxPrice,
      name: $name
    ) {
      edges {
        cursor
        node {
          uuid
          name
          price
          quantity
          slug
          images {
            edges {
              node {
                image
              }
            }
          }
          attributeGroups {
            edges {
              node {
                name
                uuid
                attributes {
                  name
                  uuid
                  values {
                    value
                    uuid
                  }
                }
              }
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
`

export const GET_PRODUCT_BY_SLUG = gql`
  query getProductBySlug(
    $slug: String!
  ) {
    products(
      slug: $slug
    ) {
      edges {
        node {
          uuid
          name
          price
          quantity
          description
          slug
          category {
            name
            slug
          }
          images {
            edges {
              node {
                image
              }
            }
          }
          attributeGroups {
            edges {
              node {
                name
                uuid
                attributes {
                  name
                  uuid
                  values {
                    value
                    uuid
                  }
                }
              }
            }
          }
          feedbacks {
            edges {
              node {
                rating
              }
            }
          }
        }
      }
    }
  }
`