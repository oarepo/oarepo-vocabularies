import {
  createSearchAppsInit,
  parseSearchAppConfigs,
  SearchAppLayout,
} from "@js/oarepo_ui";
import {
  VocabularyResultsListItemWithState,
  VocabularyButtonSidebar,
} from "./components";
import { parametrize } from "react-overridable";
const [searchAppConfig, ...otherSearchAppConfigs] = parseSearchAppConfigs();
const { overridableIdPrefix } = searchAppConfig;

const ResultsListItemWithConfig = parametrize(
  VocabularyResultsListItemWithState,
  { appName: overridableIdPrefix }
);

const SearchAppLayoutWithConfig = parametrize(SearchAppLayout, {
  hasButtonSidebar: true,
});

export const componentOverrides = {
  [`${overridableIdPrefix}.ResultsList.item`]: ResultsListItemWithConfig,
  [`${overridableIdPrefix}.SearchApp.buttonSidebarContainer`]:
    VocabularyButtonSidebar,
  [`${overridableIdPrefix}.SearchApp.layout`]: SearchAppLayoutWithConfig,
};
createSearchAppsInit({ componentOverrides });
