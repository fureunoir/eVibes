import {useMutation} from "@vue/apollo-composable";
import {GET_ORDERS} from "@/graphql/queries/orders.js";
import {useCartStore} from "@/stores/cart.js";

export function usePendingOrder() {
  const cartStore = useCartStore()

  const { mutate: pendingOrderMutation } = useMutation(GET_ORDERS);

  async function getPendingOrder(userEmail) {
    const response = await pendingOrderMutation({
      status: "PENDING",
      userEmail
    });

    if (!response.errors) {
      cartStore.setCurrentOrders(response.data.orders.edges[0].node)
    }
  }

  return {
    getPendingOrder
  };
}