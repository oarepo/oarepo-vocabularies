import React, { useState } from "react";
import PropTypes from "prop-types";
import { Grid } from "semantic-ui-react";
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

export const VocabularyRemoteSearchAppLayout = ({
  vocabulary,
  overriddenComponents = {},
  handleSelect = () => {},
}) => {
  const [source, setSource] = useState(SearchSource.INTERNAL);

  const defaultOverridenComponents = {
    "VocabularyRemoteSelect.int.ResultsList.item": "bla",
  };

  const findMore = () => {
    if (source === SearchSource.INTERNAL) {
      setSource(SearchSource.EXTERNAL);
    }
  };

  return (
    <MultiSourceSearchApp
      // Setting key here is important to re-mount SearchKit app with new source
      key={source}
      source={source}
      vocabulary={vocabulary}
      overriddenComponents={overriddenComponents}
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
  );
};

VocabularyRemoteSearchAppLayout.propTypes = {
  vocabulary: PropTypes.string.isRequired,
  overriddenComponents: PropTypes.object,
  handleSelect: PropTypes.func,
};

VocabularyRemoteSearchAppLayout.defaultProps = {
  overriddenComponents: {},
  handleSelect: () => {},
};

export default VocabularyRemoteSearchAppLayout;
