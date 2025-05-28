import gql from 'graphql-tag'
import {ORDER_FRAGMENT} from "@/graphql/fragments/orders.fragment.js";

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
        ...Order
      }
    }
  }
  ${ORDER_FRAGMENT}
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
        ...Order
      }
    }
  }
  ${ORDER_FRAGMENT}
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
        ...Order
      }
    }
  }
  ${ORDER_FRAGMENT}
`

export const REMOVE_ALL_FROM_CART = gql`
  mutation removeAllFromCart(
      $orderUuid: String!
  ) {
    removeAllOrderProducts(
        orderUuid: $orderUuid
    ) {
      order {
        ...Order
      }
    }
  }
  ${ORDER_FRAGMENT}
`