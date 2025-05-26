import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client/core'
import { setContext } from '@apollo/client/link/context'
import {DEFAULT_LOCALE, LOCALE_STORAGE_LOCALE_KEY} from "@/config/index.js";
import {computed} from "vue";
import { useAuthStore } from "@/stores/auth.js";

const httpLink = createHttpLink({
  uri: 'https://api.' + import.meta.env.EVIBES_BASE_DOMAIN + '/graphql/',
});

const userLocale = computed(() => {
  return localStorage.getItem(LOCALE_STORAGE_LOCALE_KEY)
});

export const createApolloClient = () => {
  const authStore = useAuthStore()

  const accessToken = computed(() => {
    return authStore.accessToken
  })

  const authLink = setContext((_, { headers }) => {
    const baseHeaders = {
      ...headers,
      "Accept-language": userLocale.value ? userLocale.value : DEFAULT_LOCALE,
    };

    if (accessToken.value) {
      baseHeaders["X-EVIBES-AUTH"] = `Bearer ${accessToken.value}`;
    }

    return { headers: baseHeaders };
  })

  return new ApolloClient({
    link: authLink.concat(httpLink),
    cache: new InMemoryCache(),
    defaultOptions: {
      watchQuery: {
        fetchPolicy: 'cache-and-network',
      }
    }
  })
}