import gql from 'graphql-tag'

export const GET_ORDERS = gql`
  query getOrders(
    $status: String!, 
    $userEmail: String!
  ) {
    orders(
        status: $status,
        orderBy: "-buyTime", 
        userEmail: $userEmail
    ) {
      edges {
        node {
          totalPrice
          uuid
          status
          buyTime
          totalPrice
          humanReadableId
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
  }
`