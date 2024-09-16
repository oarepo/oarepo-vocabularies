import React from "react";
import Overridable from "react-overridable";
import { withState, ResultsLoader } from "react-searchkit";
import { List, Header } from "semantic-ui-react";
import { ShouldRender } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { InternalResultListItem } from "./InternalResultListItem";
import { SearchSource } from "./constants";
import { featuredFilterActive } from "./util";
import { useFieldValue } from "./context";

export const VocabularyRemoteResultsLoader = withState(
  ({ currentQueryState, currentResultsState: results, children }) => {
    return (
      <ShouldRender
        condition={
          currentQueryState.queryString !== "" ||
          (results.data.total > 0 && featuredFilterActive(currentQueryState))
        }
      >
        <ResultsLoader>{children}</ResultsLoader>
      </ShouldRender>
    );
  }
);

export const VocabularyRemoteSearchResults = withState(
  ({
    currentResultsState: results,
    currentQueryState,
    handleSelect,
    findMore,
    source,
  }) => {
    const notEnoughResults = currentQueryState.size > results.data.hits.length;
    const { value: fieldValue, multiple } = useFieldValue();
    const canFindMore =
      source === SearchSource.INTERNAL &&
      !featuredFilterActive(currentQueryState);

    React.useEffect(() => {
      if (notEnoughResults && results && results.data.total === 0) {
        findMore(currentQueryState);
      }
    }, [results]);

    const isSelected = (result) => {
      if (!fieldValue) {
        return;
      }
      if (multiple) {
        return fieldValue.map((val) => val.id).includes(result.id);
      }
      return fieldValue.id === result.id;
    };

    return (
      <List verticalAlign="middle" selection size="small">
        {results.data.hits.map((result) => {
          return (
            <Overridable
              key={result.id}
              id={`VocabularyRemoteSelect.${source}.ResultsList.item`}
              result={result}
              selected={isSelected(result)}
            >
              <InternalResultListItem
                result={result}
                selected={isSelected(result)}
                handleSelect={handleSelect}
              />
            </Overridable>
          );
        })}
        {notEnoughResults && canFindMore && (
          <List.Item
            className="search-result-item"
            key="_find-more"
            onClick={() => findMore(currentQueryState)}
          >
            <Header color="blue" className="mb-5" size="small">
              {i18next.t("Find more records …")}
            </Header>
          </List.Item>
        )}
      </List>
    );
  }
);

VocabularyRemoteSearchResults.propTypes = {};

VocabularyRemoteSearchResults.defaultProps = {};

export default VocabularyRemoteSearchResults;
