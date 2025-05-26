import {useMutation} from "@vue/apollo-composable";
import {GET_WISHLIST} from "@/graphql/queries/wishlist.js";
import {useWishlistStore} from "@/stores/wishlist.js";

export function useAuthWishlist() {
  const wishlistStore = useWishlistStore()

  const { mutate: wishlistMutation } = useMutation(GET_WISHLIST);

  async function getWishlist() {
    const response = await wishlistMutation();

    if (!response.errors) {
      wishlistStore.setWishlist(response.data.wishlists.edges[0].node)
    }
  }

  return {
    getWishlist
  };
}