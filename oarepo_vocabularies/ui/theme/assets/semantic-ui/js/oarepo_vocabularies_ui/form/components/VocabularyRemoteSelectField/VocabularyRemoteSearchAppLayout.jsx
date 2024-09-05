import React, { useState } from "react";
import PropTypes from "prop-types";
import { Grid, Modal, Button } from "semantic-ui-react";
import {
  SearchBar,
  EmptyResults,
  Error,
  ResultsLoader,
  Pagination,
} from "react-searchkit";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import VocabularyRemoteSearchResults from "./VocabularyRemoteSearchResults";
import MultiSourceSearchApp from "./MultiSourceSearchApp";
import { SearchSource } from "./constants";
import { ExternalResultListItem } from "./ExternalResultListItem";

export const VocabularyRemoteSearchAppLayout = ({
  addNew,
  onSubmit,
  vocabulary,
  multiple,
  overriddenComponents = {},
  initialQueryState = {
    size: 10,
    page: 1,
    sortBy: "bestmatch",
  },
  handleSelect = () => {},
}) => {
  const [source, setSource] = useState(SearchSource.INTERNAL);
  const [queryState, setQueryState] = useState(initialQueryState);

  const defaultOverridenComponents = {
    "VocabularyRemoteSelect.ext.ResultsList.item": ExternalResultListItem,
  };

  const findMore = (previousQueryState) => {
    if (source === SearchSource.INTERNAL) {
      setSource(SearchSource.EXTERNAL);
    }
    setQueryState({ ...previousQueryState, page: 1 });
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
                  }}
                  showWhenOnlyOnePage={false}
                />
              </Grid.Column>
            </Grid.Row>
            <ResultsLoader>
              <Grid.Row>
                <Grid.Column>
                  <EmptyResults />
                  <Error />
                  <VocabularyRemoteSearchResults
                    source={source}
                    handleSelect={handleSelect}
                    findMore={findMore}
                  />
                </Grid.Column>
              </Grid.Row>
              <Grid.Row columns="equal">
                <Grid.Column
                  floated="right"
                  width={8}
                  textAlign="right"
                ></Grid.Column>
              </Grid.Row>
            </ResultsLoader>
          </Grid>
        </MultiSourceSearchApp>
      </Modal.Content>
      <Modal.Actions>
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
  multiple: PropTypes.bool,
  addNew: PropTypes.func,
  onSubmit: PropTypes.func,
};

VocabularyRemoteSearchAppLayout.defaultProps = {
  overriddenComponents: {},
  multiple: false,
  initialQueryState: {
    size: 10,
    page: 1,
    sortBy: "bestmatch",
  },
  handleSelect: () => {},
};

export default VocabularyRemoteSearchAppLayout;
