import gql from 'graphql-tag'

export const ADD_TO_CART = gql`
  mutation addToCart(
      $orderUuid: String!, 
      $productUuid: String!
  ) {
    addOrderProduct(
        orderUuid: $orderUuid, 
        productUuid: $productUuid
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

export const REMOVE_FROM_CART = gql`
  mutation removeFromCart(
      $orderUuid: String!, 
      $productUuid: String!
  ) {
    removeOrderProduct(
        orderUuid: $orderUuid, 
        productUuid: $productUuid
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

export const REMOVE_KIND_FROM_CART = gql`
  mutation removeKindFromCart(
      $orderUuid: String!, 
      $productUuid: String!
  ) {
    removeOrderProductsOfAKind(
        orderUuid: $orderUuid, 
        productUuid: $productUuid
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

export const REMOVE_ALL_FROM_CART = gql`
  mutation removeAllFromCart(
      $orderUuid: String!
  ) {
    removeAllOrderProducts(
        orderUuid: $orderUuid
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