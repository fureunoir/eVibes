import gql from 'graphql-tag'
import {CATEGORY_FRAGMENT} from "@/graphql/fragments/categories.fragment.js";

export const GET_CATEGORIES = gql`
  query getCategories {
    categories {
      edges {
        node {
          ...Category
        }
      }
    }
  }
  ${CATEGORY_FRAGMENT}
`

export const GET_CATEGORY_BY_SLUG = gql`
  query getCategoryBySlug(
    $slug: String!
  ) {
    categories(
      slug: $slug
    ) {
      edges {
        node {
          ...Category
          filterableAttributes {
            possibleValues
            attributeName
          }
          minMaxPrices {
            maxPrice
            minPrice
          }
        }
      }
    }
  }
  ${CATEGORY_FRAGMENT}
`