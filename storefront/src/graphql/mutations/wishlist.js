import gql from 'graphql-tag'

export const ADD_TO_WISHLIST = gql`
  mutation addToWishlist(
      $wishlistUuid: String!, 
      $productUuid: String!
  ) {
    addWishlistProduct(
        wishlistUuid: $wishlistUuid, 
        productUuid: $productUuid
    ) {
      wishlist {
        uuid
        products {
          edges {
            node {
              uuid
              price
              name
              description
              quantity
              slug
              images {
                edges {
                  node {
                    uuid
                    image
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

export const REMOVE_FROM_WISHLIST = gql`
  mutation removeFromWishlist(
      $wishlistUuid: String!, 
      $productUuid: String!
  ) {
    removeWishlistProduct(
        wishlistUuid: $wishlistUuid, 
        productUuid: $productUuid
    ) {
      wishlist {
        uuid
        products {
          edges {
            node {
              uuid
              price
              name
              description
              quantity
              slug
              images {
                edges {
                  node {
                    uuid
                    image
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

export const REMOVE_ALL_FROM_WISHLIST = gql`
  mutation removeAllFromCart(
      $wishlistUuid: String!
  ) {
    removeAllWishlistProducts(
        wishlistUuid: $wishlistUuid
    ) {
      order {
        status
        uuid
        totalPrice
        orderProducts {
          edges {
            node {
              uuid
              notifications
              attributes
              quantity
              status
              product {
                uuid
                price
                name
                description
                quantity
                slug
                category {
                  name
                }
                images {
                  edges {
                    node {
                      uuid
                      image
                    }
                  }
                }
                category {
                  name
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