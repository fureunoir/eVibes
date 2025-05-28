import { useLazyQuery } from "@vue/apollo-composable";
import {watchEffect} from "vue";
import {GET_LANGUAGES} from "@/graphql/queries/languages.js";
import {useLanguageStore} from "@/stores/languages.js";
import {SUPPORTED_LOCALES} from "@/config/index.js";

export function useLanguages() {
  const languageStore = useLanguageStore()

  const { result, loading, error, load } = useLazyQuery(GET_LANGUAGES);

  if (error.value) {
    console.error("useLanguages error:", error.value);
  }

  watchEffect(() => {
    if (result.value?.languages) {
      languageStore.setLanguages(
        result.value.languages.filter((locale) =>
          SUPPORTED_LOCALES.some(supportedLocale =>
            supportedLocale.code === locale.code
          )
        )
      );
    }
  });

  return {
    loading,
    error,
    getLanguages: load
  };
}