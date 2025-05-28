import { useLazyQuery } from "@vue/apollo-composable";
import {computed} from "vue";
import {GET_CATEGORIES} from "@/graphql/queries/categories.js";

export function useCategories() {
  const { result, loading, error, load } = useLazyQuery(GET_CATEGORIES);

  const categories = computed(() => result.value?.categories.edges ?? []);

  if (error.value) {
    console.error("useCategories error:", error.value);
  }

  return {
    categories,
    loading,
    error,
    getCategories: load
  };
}