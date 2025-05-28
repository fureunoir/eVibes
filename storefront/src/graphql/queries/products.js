import gql from 'graphql-tag'
import {PRODUCT_FRAGMENT} from "@/graphql/fragments/products.fragment.js";

export const GET_PRODUCTS = gql`
  query getProducts(
    $after: String,
    $first: Int,
    $categorySlugs: String,
    $orderBy: String,
    $minPrice: Decimal,
    $maxPrice: Decimal,
    $name: String
  ) {
    products(
      after: $after,
      first: $first,
      categorySlugs: $categorySlugs,
      orderBy: $orderBy,
      minPrice: $minPrice,
      maxPrice: $maxPrice,
      name: $name
    ) {
      edges {
        cursor
        node {
          ...Product
        }
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
  ${PRODUCT_FRAGMENT}
`

export const GET_PRODUCT_BY_SLUG = gql`
  query getProductBySlug(
    $slug: String!
  ) {
    products(
      slug: $slug
    ) {
      edges {
        node {
          ...Product
        }
      }
    }
  }
  ${PRODUCT_FRAGMENT}
`