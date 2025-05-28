import gql from 'graphql-tag'

export const PRODUCT_FRAGMENT = gql`
  fragment Product on ProductType {
    uuid
    name
    price
    quantity
    slug
    category {
      name
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
  }
`