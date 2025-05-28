import gql from 'graphql-tag'
import {WISHLIST_FRAGMENT} from "@/graphql/fragments/wishlist.fragment.js";

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
        ...Wishlist
      }
    }
  }
  ${WISHLIST_FRAGMENT}
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
        ...Wishlist
      }
    }
  }
  ${WISHLIST_FRAGMENT}
`

export const REMOVE_ALL_FROM_WISHLIST = gql`
  mutation removeAllFromWishlist(
      $wishlistUuid: String!
  ) {
    removeAllWishlistProducts(
        wishlistUuid: $wishlistUuid
    ) {
      wishlist {
        ...Wishlist
      }
    }
  }
  ${WISHLIST_FRAGMENT}
`