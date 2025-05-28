import gql from 'graphql-tag'
import {WISHLIST_FRAGMENT} from "@/graphql/fragments/wishlist.fragment.js";

export const GET_WISHLIST = gql`
  query getWishlist {
    wishlists {
      edges {
        node {
          ...Wishlist
        }
      }
    }
  }
  ${WISHLIST_FRAGMENT}
`