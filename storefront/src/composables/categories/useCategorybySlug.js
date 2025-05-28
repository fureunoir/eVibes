import { useLazyQuery } from "@vue/apollo-composable";
import {computed} from "vue";
import {GET_CATEGORY_BY_SLUG} from "@/graphql/queries/categories.js";

export function usePostbySlug() {
  const { result, loading, error, load } = useLazyQuery(GET_CATEGORY_BY_SLUG);

  const category = computed(() => result.value?.categories.edges[0].node ?? []);

  if (error.value) {
    console.error("usePostbySlug error:", error.value);
  }

  const getCategory = (slug) => {
    return load(null, { slug });
  };

  return {
    category,
    loading,
    error,
    getCategory
  };
}