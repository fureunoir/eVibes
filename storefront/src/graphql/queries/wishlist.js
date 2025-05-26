import gql from 'graphql-tag'

export const GET_WISHLIST = gql`
  query getWishlist {
    wishlists {
      edges {
        node {
          uuid
          products {
            edges {
              node {
                uuid
                price
                name
                description
                slug
                images {
                  edges {
                    node {
                      uuid
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
          }
        }
      }
    }
  }
`