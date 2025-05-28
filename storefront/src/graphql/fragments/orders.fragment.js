import gql from 'graphql-tag'
import {PRODUCT_FRAGMENT} from "@/graphql/fragments/products.fragment.js";

export const ORDER_FRAGMENT = gql`
  fragment Order on OrderType {
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
            ...Product
          }
        }
      }
    }
  }
  ${PRODUCT_FRAGMENT}
`