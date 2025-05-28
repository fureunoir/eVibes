import { useLazyQuery } from "@vue/apollo-composable";
import {computed} from "vue";
import {GET_PRODUCT_BY_SLUG} from "@/graphql/queries/products.js";

export function useProductbySlug() {
  const { result, loading, error, load } = useLazyQuery(GET_PRODUCT_BY_SLUG);

  const product = computed(() => result.value?.products.edges[0].node ?? []);

  if (error.value) {
    console.error("useProductbySlug error:", error.value);
  }

  const getProduct = (slug) => {
    return load(null, { slug });
  };

  return {
    product,
    loading,
    error,
    getProduct
  };
}