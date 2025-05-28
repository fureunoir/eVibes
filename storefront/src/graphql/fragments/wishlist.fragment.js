import gql from 'graphql-tag'
import {PRODUCT_FRAGMENT} from "@/graphql/fragments/products.fragment.js";

export const WISHLIST_FRAGMENT = gql`
  fragment Wishlist on WishlistType {
    uuid
    products {
      edges {
        node {
          ...Product
        }
      }
    }
  }
  ${PRODUCT_FRAGMENT}
`