import { useLazyQuery } from "@vue/apollo-composable";
import {GET_POST_BY_SLUG} from "@/graphql/queries/blog.js";
import {computed} from "vue";

export function usePostbySlug() {
  const { result, loading, error, load } = useLazyQuery(GET_POST_BY_SLUG);

  const post = computed(() => result.value?.posts.edges[0].node ?? []);

  if (error.value) {
    console.error("usePostbySlug error:", error.value);
  }

  const getPost = (slug) => {
    return load(null, { slug });
  };

  return {
    post,
    loading,
    error,
    getPost
  };
}