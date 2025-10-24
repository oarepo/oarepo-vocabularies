import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  SearchAppLayout,
} from "@js/oarepo_ui/search";
import {
  VocabularyResultsListItemWithState,
  VocabularyButtonSidebar,
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
  [`${overridableIdPrefix}.SearchApp.buttonSidebarContainer`]:
    VocabularyButtonSidebar,
  [`${overridableIdPrefix}.SearchApp.layout`]: SearchAppLayoutWithConfig,
};

createSearchAppsInit({ componentOverrides });
