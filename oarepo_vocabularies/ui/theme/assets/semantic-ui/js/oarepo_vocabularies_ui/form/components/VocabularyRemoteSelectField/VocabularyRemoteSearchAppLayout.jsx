import React, { useState } from "react";
import PropTypes from "prop-types";
import { Grid, Modal, Button } from "semantic-ui-react";
import { SearchBar, EmptyResults, Error, Pagination } from "react-searchkit";
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
    filters: [],
  },
  handleSelect = () => {},
}) => {
  const [source, setSource] = useState(SearchSource.INTERNAL);
  const [queryState, setQueryState] = useState(initialQueryState);
  const { multiple } = useFieldValue();

  const defaultOverridenComponents = {
    "EmptyResults.element": ExternalEmptyResultsElement,
    "VocabularyRemoteSelect.ext.ResultsList.item": ExternalResultListItem,
  };

  const findMore = (previousQueryState) => {
    if (source === SearchSource.INTERNAL) {
      setSource(SearchSource.EXTERNAL);
    }
    const newQueryState = { ...previousQueryState, filters: [], page: 1 };
    setQueryState(newQueryState);
  };

  const resetSearch = () => {
    setQueryState(initialQueryState);
    setSource(SearchSource.INTERNAL);
  };

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
                <SearchBar
                  placeholder={i18next.t("Search")}
                  autofocus
                  clearable
                  actionProps={{
                    icon: "search",
                    content: null,
                    className: "search",
                  }}
                />
              </Grid.Column>
              <Grid.Column>
                <Pagination
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
        <Button
          icon="plus"
          content={i18next.t("Add new")}
          onClick={() => addNew()}
        />
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

VocabularyRemoteSearchAppLayout.propTypes = {
  vocabulary: PropTypes.string.isRequired,
  overriddenComponents: PropTypes.object,
  initialQueryState: PropTypes.object,
  handleSelect: PropTypes.func,
  addNew: PropTypes.func,
  onSubmit: PropTypes.func,
  extraActions: PropTypes.node,
};

VocabularyRemoteSearchAppLayout.defaultProps = {
  overriddenComponents: {},
  initialQueryState: {
    size: 10,
    page: 1,
    sortBy: "bestmatch",
    filters: [],
  },
  handleSelect: () => {},
};

export default VocabularyRemoteSearchAppLayout;
