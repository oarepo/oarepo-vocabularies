import React, { useMemo } from "react";
import PropTypes from "prop-types";
import { OverridableContext } from "react-overridable";
import { Container, Grid, Header } from "semantic-ui-react";
import {
  EmptyResults,
  Error,
  ReactSearchKit,
  ResultsLoader,
  withState,
  InvenioSearchApi,
} from "react-searchkit";
import { Results } from "./Results";
import { VocabularyResultsListItemWithState } from "../search/components";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components";

const OnResults = withState(Results);

const CountElement = ({ totalResults }) => {
  return (
    <Header as="h3">
      {i18next.t("totalDescendants", { count: totalResults })}
    </Header>
  );
};

CountElement.propTypes = {
  totalResults: PropTypes.number.isRequired,
};

const overriddenComponents = {
  "ResultsList.item": VocabularyResultsListItemWithState,
  "Count.element": CountElement,
};

// HOC that will have access to the query results and wrap the app, so that I can render it conditionally only if there are hits
const AppWrapper = withState(({ currentResultsState, children }) => {
  return currentResultsState.data.total ? { children } : null;
});

export const App = ({ appConfig }) => {
  const {
    searchApi,
    initialQueryState,
    defaultSortingOnEmptyQueryString,
    sortOptions,
    paginationOptions,
  } = appConfig;

  const searchConfigurationValue = useMemo(() => {
    return { ...appConfig };
  }, [appConfig]);

  return (
    <OverridableContext.Provider value={overriddenComponents}>
      <SearchConfigurationContext.Provider value={searchConfigurationValue}>
        <ReactSearchKit
          searchApi={new InvenioSearchApi(searchApi)}
          initialQueryState={initialQueryState}
          urlHandlerApi={{ enabled: false }}
          defaultSortingOnEmptyQueryString={defaultSortingOnEmptyQueryString}
        >
          <AppWrapper>
            <Container>
              <Grid relaxed centered>
                <Grid.Row>
                  <Grid.Column width={16}>
                    <ResultsLoader>
                      <EmptyResults />
                      <Error />
                      <OnResults
                        sortValues={sortOptions}
                        resultsPerPageValues={paginationOptions.resultsPerPage}
                        currentFacet={initialQueryState.filters}
                      />
                    </ResultsLoader>
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Container>
          </AppWrapper>
        </ReactSearchKit>
      </SearchConfigurationContext.Provider>
    </OverridableContext.Provider>
  );
};

App.propTypes = {
  appConfig: PropTypes.shape({
    searchApi: PropTypes.object.isRequired,
    initialQueryState: PropTypes.shape({
      queryString: PropTypes.string,
      suggestions: PropTypes.array,
      sortBy: PropTypes.string,
      sortOrder: PropTypes.string,
      page: PropTypes.number,
      size: PropTypes.number,
      filters: PropTypes.array,
      hiddenParams: PropTypes.array,
      layout: PropTypes.oneOf(["list", "grid"]),
    }),
    defaultSortingOnEmptyQueryString: PropTypes.shape({
      sortBy: PropTypes.string,
      sortOrder: PropTypes.string,
    }),
    sortOptions: PropTypes.arrayOf(PropTypes.object),
    paginationOptions: PropTypes.shape({
      defaultValue: PropTypes.number,
      resultsPerPage: PropTypes.array,
    }),
  }).isRequired,
};
