import React from "react";
import PropTypes from "prop-types";
import { Grid } from "semantic-ui-react";
import {
  InvenioSearchApi,
  ReactSearchKit,
  SearchBar,
  EmptyResults,
  Error,
  ResultsPerPage,
  ResultsLoader,
  Pagination,
} from "react-searchkit";
import { OverridableContext } from "react-overridable";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import VocabularyRemoteSearchResults from "./VocabularyRemoteSearchResults";

export const VocabularyRemoteSearchAppLayout = ({
  vocabulary,
  overriddenComponents = {},
}) => {
  const searchConfig = {
    searchApi: {
      axios: {
        headers: {
          Accept: "application/vnd.inveniordm.v1+json",
        },
        url: `/api/vocabularies/${vocabulary}`,
      },
    },
    initialQueryState: {
      size: 10,
      page: 1,
      sortBy: "bestmatch",
    },
    // paginationOptions: {
    //   defaultValue: 10,
    //   resultsPerPage: [
    //     { text: "10", value: 10 },
    //     { text: "20", value: 20 },
    //     { text: "50", value: 50 },
    //   ],
    // },
  };

  const searchApi = new InvenioSearchApi(searchConfig.searchApi);
  const handleSelect = (value) => {
    console.log("SELECTED", value);
  };

  return (
    <OverridableContext.Provider value={overriddenComponents}>
      <ReactSearchKit
        searchApi={searchApi}
        urlHandlerApi={{ enabled: false }}
        initialQueryState={{
          ...searchConfig.initialQueryState,
          filters: [],
        }}
      >
        <Grid>
          <Grid.Row>
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
          </Grid.Row>
          <ResultsLoader>
            <Grid.Row>
              <Grid.Column>
                <EmptyResults />
                <Error />
                <VocabularyRemoteSearchResults handleSelect={handleSelect} />
              </Grid.Column>
            </Grid.Row>
            <Grid.Row columns="equal">
              <Grid.Column floated="right" width={8} textAlign="right">
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
          </ResultsLoader>
        </Grid>
      </ReactSearchKit>
    </OverridableContext.Provider>
  );
};

VocabularyRemoteSearchAppLayout.propTypes = {
  vocabulary: PropTypes.string.isRequired,
  overriddenComponents: PropTypes.object,
};

VocabularyRemoteSearchAppLayout.defaultProps = {};

export default VocabularyRemoteSearchAppLayout;
