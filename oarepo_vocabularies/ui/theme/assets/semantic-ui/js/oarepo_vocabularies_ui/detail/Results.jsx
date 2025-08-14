import PropTypes from "prop-types";
import React from "react";
import { Grid } from "semantic-ui-react";
import {
  Pagination,
  ResultsMultiLayout,
  ResultsPerPage,
} from "react-searchkit";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { ResultCountWithState } from "@js/oarepo_ui/search";

const resultsPerPageLabel = (cmp) => (
  <React.Fragment>
    {cmp} {i18next.t("resultsPerPage")}
  </React.Fragment>
);

export const Results = ({ resultsPerPageValues, currentResultsState }) => {
  const { data } = currentResultsState;
  const { total } = data;

  return total ? (
    <React.Fragment>
      <ResultCountWithState />
      <ResultsMultiLayout />
      <Grid relaxed verticalAlign="middle" textAlign="center">
        <Grid.Row verticalAlign="middle">
          <Grid.Column className="computer tablet only" width={4} />
          <Grid.Column
            className="computer tablet only"
            width={8}
            textAlign="center"
          >
            <Pagination
              showWhenOnlyOnePage={false}
              options={{
                size: "mini",
                showFirst: false,
                showLast: false,
              }}
            />
          </Grid.Column>
          <Grid.Column className="mobile only" width={16} textAlign="center">
            <Pagination
              showWhenOnlyOnePage={false}
              options={{
                boundaryRangeCount: 0,
                showFirst: false,
                showLast: false,
              }}
            />
          </Grid.Column>
          <Grid.Column
            className="computer tablet only "
            textAlign="right"
            width={4}
          >
            <ResultsPerPage
              showWhenOnlyOnePage={false}
              values={resultsPerPageValues}
              label={resultsPerPageLabel}
            />
          </Grid.Column>
          <Grid.Column
            className="mobile only mt-10"
            textAlign="center"
            width={16}
          >
            <ResultsPerPage
              showWhenOnlyOnePage={false}
              values={resultsPerPageValues}
              label={resultsPerPageLabel}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </React.Fragment>
  ) : null;
};

Results.propTypes = {
  currentResultsState: PropTypes.object.isRequired,
  resultsPerPageValues: PropTypes.array.isRequired,
};
