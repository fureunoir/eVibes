import gql from 'graphql-tag'
import {ORDER_FRAGMENT} from "@/graphql/fragments/orders.fragment.js";

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
          ...Order
        }
      }
    }
  }
  ${ORDER_FRAGMENT}
`