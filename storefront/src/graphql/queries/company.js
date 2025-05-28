import gql from 'graphql-tag'
import {COMPANY_FRAGMENT} from "@/graphql/fragments/company.fragment.js";

export const GET_COMPANY_INFO = gql`
  query getCompanyInfo {
    parameters {
      ...Company
    }
  }
  ${COMPANY_FRAGMENT}
`