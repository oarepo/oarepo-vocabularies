import React from "react";
import Overridable from "react-overridable";
import { withState, ResultsLoader } from "react-searchkit";
import { List, Header, Grid } from "semantic-ui-react";
import { ShouldRender } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { InternalResultListItem } from "./InternalResultListItem";
import { SearchSource } from "./constants";
import { featuredFilterActive } from "./util";
import { useFieldValue } from "./context";
import { OptionsLoadingSkeleton } from "@js/oarepo_vocabularies";

export const VocabularyRemoteResultsLoader = withState(
  ({ currentQueryState, currentResultsState: results, children }) => {
    console.log({ currentQueryState, results });

    return (
      <>
        <ShouldRender
          condition={
            currentQueryState.queryString !== "" ||
            (results.data.total > 0 && featuredFilterActive(currentQueryState))
          }
        >
          <ResultsLoader>{children}</ResultsLoader>
        </ShouldRender>
        <ShouldRender
          condition={
            currentQueryState.queryString === "" &&
            currentQueryState.suggestionString !== "" &&
            currentQueryState.suggestions.length > 0
          }
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
    currentQueryState,
    handleSelect,
    findMore,
    source,
  }) => {
    const _results =
      currentQueryState.suggestions.length > 0
        ? currentQueryState.suggestions
        : results.data.hits;
    const notEnoughResults = currentQueryState.size > _results.length;
    const { value: fieldValue, multiple } = useFieldValue();
    const canFindMore =
      source === SearchSource.INTERNAL &&
      !featuredFilterActive(currentQueryState);

    React.useEffect(() => {
      if (
        notEnoughResults &&
        _results &&
        (results.data.total === 0 || _results.length === 0)
      ) {
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
        {results.loading && <OptionsLoadingSkeleton />}
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

VocabularyRemoteSearchResults.propTypes = {};

VocabularyRemoteSearchResults.defaultProps = {};

export default VocabularyRemoteSearchResults;
