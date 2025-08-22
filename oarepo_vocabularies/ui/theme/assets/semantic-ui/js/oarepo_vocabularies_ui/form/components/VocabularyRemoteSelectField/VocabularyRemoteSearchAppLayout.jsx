import React, { useState } from "react";
import PropTypes from "prop-types";
import { Grid, Modal, Button } from "semantic-ui-react";
import {
  AutocompleteSearchBar,
  EmptyResults,
  Error,
  Pagination,
  withState,
} from "react-searchkit";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import VocabularyRemoteSearchResults, {
  VocabularyRemoteResultsLoader,
} from "./VocabularyRemoteSearchResults";
import MultiSourceSearchApp from "./MultiSourceSearchApp";
import { SearchSource } from "./constants";
import { ExternalResultListItem } from "./ExternalResultListItem";
import {
  ExternalEmptyResultsElement,
  ExternalEmptyResults,
} from "./ExternalEmptyResults";
import VocabularyRemoteFeaturedResults from "./VocabularyRemoteFeaturedResults";
import { useFieldValue } from "./context";
import { inSuggestMode } from "./util";
import ResultsLoadingSkeleton from "./ResultsLoadingSkeleton";

const ContextAwarePagination = withState(
  ({ currentQueryState, ...paginationProps }) => {
    // Suggestions are always fixed to one-page size
    return (
      !inSuggestMode(currentQueryState) && <Pagination {...paginationProps} />
    );
  }
);

export const VocabularyRemoteSearchAppLayout = ({
  addNew,
  onSubmit,
  vocabulary,
  extraActions,
  overriddenComponents = {},
  initialQueryState = {
    size: 10,
    page: 1,
    sortBy: "bestmatch",
    queryString: "",
    filters: [["tags", "featured"]],
  },
  allowAdditions = true,
  handleSelect = () => {},
}) => {
  const [source, setSource] = useState(SearchSource.INTERNAL);
  const [queryState, setQueryState] = useState(initialQueryState);
  const { multiple } = useFieldValue();
  const searchbarContainer = React.useRef(null);

  const defaultOverridenComponents = {
    "EmptyResults.element": ExternalEmptyResultsElement,
    "VocabularyRemoteSelect.ext.ResultsList.item": ExternalResultListItem,
    "AutocompleteSearchBar.suggestions": () => null,
  };

  const findMore = React.useCallback(
    (previousQueryState) => {
      if (source === SearchSource.INTERNAL) {
        setSource(SearchSource.EXTERNAL);
      }
      const newQueryState = { ...previousQueryState, filters: [], page: 1 };
      setQueryState(newQueryState);
    },
    [source, setSource, setQueryState]
  );

  const resetSearch = () => {
    setQueryState(initialQueryState);
    setSource(SearchSource.INTERNAL);
  };

  React.useEffect(() => {
    // There's currently no other more sane way to focus that component's input
    if (searchbarContainer.current) {
      const searchbarInput = searchbarContainer.current.querySelector("input");
      if (searchbarInput) searchbarInput.focus();
    }
  }, []);

  return (
    <>
      <Modal.Content>
        <MultiSourceSearchApp
          // Setting key here is important to re-mount SearchKit app with new source
          key={source}
          source={source}
          vocabulary={vocabulary}
          queryState={queryState}
          overriddenComponents={{
            ...defaultOverridenComponents,
            ...overriddenComponents,
          }}
        >
          <Grid stackable>
            <Grid.Row verticalAlign="middle" columns={2}>
              <Grid.Column width={8} floated="left" verticalAlign="middle">
                <div className="ui form" ref={searchbarContainer}>
                  <AutocompleteSearchBar
                    placeholder={i18next.t("Search")}
                    autofocus
                    clearable
                  />
                </div>
              </Grid.Column>
              <Grid.Column>
                <ContextAwarePagination
                  options={{
                    size: "mini",
                    showFirst: false,
                    showLast: false,
                    siblingRangeCount: 0,
                  }}
                  showWhenOnlyOnePage={false}
                />
              </Grid.Column>
            </Grid.Row>
            <ResultsLoadingSkeleton />
            <VocabularyRemoteFeaturedResults source={source} />
            <VocabularyRemoteResultsLoader>
              <Grid.Row className="scrolling content">
                <Grid.Column>
                  <Error />
                  {source === SearchSource.EXTERNAL && (
                    <>
                      <EmptyResults />
                      <ExternalEmptyResults resetSearch={resetSearch} />
                    </>
                  )}
                  <VocabularyRemoteSearchResults
                    source={source}
                    handleSelect={handleSelect}
                    findMore={findMore}
                  />
                </Grid.Column>
              </Grid.Row>
            </VocabularyRemoteResultsLoader>
          </Grid>
        </MultiSourceSearchApp>
      </Modal.Content>
      <Modal.Actions>
        {extraActions}
        {allowAdditions && (
          <Button
            icon="plus"
            content={i18next.t("Add new")}
            onClick={() => addNew()}
          />
        )}
        {multiple && (
          <Button
            type="submit"
            content={i18next.t("Confirm")}
            icon="checkmark"
            onClick={() => onSubmit()}
            secondary
          />
        )}
      </Modal.Actions>
    </>
  );
};

/* eslint-disable react/require-default-props */
VocabularyRemoteSearchAppLayout.propTypes = {
  vocabulary: PropTypes.string.isRequired,
  overriddenComponents: PropTypes.object,
  initialQueryState: PropTypes.object,
  handleSelect: PropTypes.func,
  addNew: PropTypes.func,
  onSubmit: PropTypes.func,
  extraActions: PropTypes.node,
  allowAdditions: PropTypes.bool,
};
/* eslint-enable react/require-default-props */

export default VocabularyRemoteSearchAppLayout;
