import { ref } from 'vue';
import { useQuery } from '@vue/apollo-composable';
import {GET_PRODUCTS} from "@/graphql/queries/products.js";

export function useProducts() {
  const products = ref([]);
  const pageInfo = ref([]);
  const loading = ref(false);

  const getProducts = async (params = {}) => {
    loading.value = true;

    const defaults = {
      first: 12
    };

    const variables = {};

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        variables[key] = value;
      }
    });

    Object.entries(defaults).forEach(([key, value]) => {
      if (!(key in variables)) {
        variables[key] = value;
      }
    });

    try {
      const { onResult } = useQuery(GET_PRODUCTS, variables);

      onResult(result => {
        if (result.data && result.data.products) {
          products.value = result.data.products.edges;
          pageInfo.value = result.data.products.pageInfo;
        }
        loading.value = false;
      });
    } catch (error) {
      console.error('useProducts error:', error);
      loading.value = false;
    }
  };

  return {
    products,
    pageInfo,
    loading,
    getProducts
  };
}