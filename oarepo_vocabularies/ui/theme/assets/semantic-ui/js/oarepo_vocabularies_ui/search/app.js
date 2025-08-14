import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  SearchAppLayout,
} from "@js/oarepo_ui/search";
import {
  VocabularyResultsListItemWithState,
  VocabularyButtonSidebar,
  NamesResultsListItem,
  AwardsResultsListItem,
  FundersResultsListItem,
  AffiliationsResultsListItem,
} from "./components";
import { parametrize } from "react-overridable";

const [{ overridableIdPrefix }] = parseSearchAppConfigs();

const ResultsListItemWithConfig = parametrize(
  VocabularyResultsListItemWithState,
  { appName: overridableIdPrefix }
);

const SearchAppLayoutWithConfig = parametrize(SearchAppLayout, {
  hasButtonSidebar: true,
});
// cannot use dynamic resultlistitem, because not all vocabularies have "type" property so using URL instead
export const componentOverrides = {
  [`${overridableIdPrefix}.ResultsList.item`]: ResultsListItemWithConfig,
  [`${overridableIdPrefix}.ResultsList.item.names`]: NamesResultsListItem,
  [`${overridableIdPrefix}.ResultsList.item.awards`]: AwardsResultsListItem,
  [`${overridableIdPrefix}.ResultsList.item.funders`]: FundersResultsListItem,
  [`${overridableIdPrefix}.ResultsList.item.affiliations`]:
    AffiliationsResultsListItem,
  [`${overridableIdPrefix}.SearchApp.buttonSidebarContainer`]:
    VocabularyButtonSidebar,

  [`${overridableIdPrefix}.SearchApp.layout`]: SearchAppLayoutWithConfig,
};
createSearchAppsInit({ componentOverrides });
