import { useLazyQuery } from "@vue/apollo-composable";
import { GET_POSTS } from "@/graphql/queries/blog.js";
import {computed} from "vue";

export function usePosts() {
  const { result, loading, error, load } = useLazyQuery(GET_POSTS);

  const posts = computed(() => result.value?.posts.edges ?? []);

  if (error.value) {
    console.error("usePosts error:", error.value);
  }

  return {
    posts,
    loading,
    error,
    getPosts: load
  };
}