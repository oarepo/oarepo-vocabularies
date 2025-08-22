import React from "react";
import Overridable from "react-overridable";
import { withState, ResultsLoader } from "react-searchkit";
import { List, Header } from "semantic-ui-react";
import { ShouldRender } from "@js/oarepo_ui/search";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { InternalResultListItem } from "./InternalResultListItem";
import { SearchSource } from "./constants";
import { featuredFilterActive, inSuggestMode } from "./util";
import { useFieldValue } from "./context";
import PropTypes from "prop-types";

export const VocabularyRemoteResultsLoader = withState(
  ({ currentQueryState, currentResultsState: results, children }) => {
    return (
      <>
        <ShouldRender
          condition={!results.loading && !inSuggestMode(currentQueryState)}
        >
          <ResultsLoader>{children}</ResultsLoader>
        </ShouldRender>
        <ShouldRender
          condition={!results.loading && inSuggestMode(currentQueryState)}
        >
          {children}
        </ShouldRender>
      </>
    );
  }
);

export const VocabularyRemoteSearchResults = withState(
  ({
    currentResultsState: results,
    updateQueryState,
    currentQueryState,
    handleSelect,
    findMore,
    source,
  }) => {
    const { suggestionString, queryString } = currentQueryState;
    const _results = inSuggestMode(currentQueryState)
      ? currentQueryState.suggestions
      : results.data.hits;
    const notEnoughResults = currentQueryState.size > _results.length;
    const { value: fieldValue, multiple } = useFieldValue();
    const canFindMore =
      source === SearchSource.INTERNAL &&
      !inSuggestMode(currentQueryState) &&
      !featuredFilterActive(currentQueryState);

    React.useEffect(() => {
      if (
        notEnoughResults &&
        _results &&
        canFindMore &&
        (results.data.total === 0 || _results.length === 0)
      ) {
        findMore(currentQueryState);
      }
    }, [
      results,
      suggestionString,
      _results,
      canFindMore,
      notEnoughResults,
      currentQueryState,
      findMore,
    ]);

    React.useEffect(() => {
      if (
        (queryString !== "" || suggestionString !== "") &&
        featuredFilterActive(currentQueryState)
      ) {
        updateQueryState({
          ...currentQueryState,
          suggestionString: "",
          filters: [],
        });
      }
    }, [queryString, suggestionString, currentQueryState, updateQueryState]);

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
        {_results.map((result) => {
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
        {!results.loading && notEnoughResults && canFindMore && (
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
VocabularyRemoteSearchResults.propTypes = {
  currentResultsState: PropTypes.shape({
    loading: PropTypes.bool.isRequired,
    data: PropTypes.shape({
      hits: PropTypes.array.isRequired,
      total: PropTypes.number,
    }).isRequired,
  }).isRequired,
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  handleSelect: PropTypes.func.isRequired,
  findMore: PropTypes.func.isRequired,
  source: PropTypes.oneOf(Object.values(SearchSource)).isRequired,
};
export default VocabularyRemoteSearchResults;
