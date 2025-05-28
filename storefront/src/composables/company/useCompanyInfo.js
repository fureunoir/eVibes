import {useLazyQuery} from "@vue/apollo-composable";
import {GET_COMPANY_INFO} from "@/graphql/queries/company.js";
import {useCompanyStore} from "@/stores/company.js";
import {watchEffect} from "vue";

export function useCompanyInfo() {
  const companyStore = useCompanyStore()

  const { result, loading, error, load } = useLazyQuery(GET_COMPANY_INFO);

  if (error.value) {
    console.error("useCompanyInfo error:", error.value);
  }

  watchEffect(() => {
    if (result.value?.parameters) {
      companyStore.setCompanyInfo(result.value.parameters);
    }
  });

  return {
    loading,
    error,
    getCompanyInfo: load
  };
}