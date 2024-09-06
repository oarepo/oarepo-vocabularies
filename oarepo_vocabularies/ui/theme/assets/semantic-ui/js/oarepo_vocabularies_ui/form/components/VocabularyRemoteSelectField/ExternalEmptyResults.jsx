import * as React from "react";
import _join from "lodash/join";
import { withState } from "react-searchkit";
import { Segment, Icon, Header, Button } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_ui/i18next";
import _isEmpty from "lodash/isEmpty";
import { ShouldRender } from "@js/oarepo_ui";

export const ExternalEmptyResultsElement = ({
  queryString,
  resetQuery,
  extraContent,
  userSelectionFilters,
}) => (
  <Segment placeholder textAlign="center">
    <Header icon>
      <Icon name="search" />
    </Header>
    {queryString && (
      <em>
        {i18next.t("We couldn't find any matches for ")} "{queryString}"
      </em>
    )}
    <br />
    {extraContent}
  </Segment>
);

export const ExternalEmptyResults = withState(
  ({
    currentResultsState: {
      loading,
      error,
      data: { total: totalResults },
    },
    resetSearch,
  }) => (
    <ShouldRender condition={!loading && _isEmpty(error) && totalResults === 0}>
      <Segment attached="bottom" textAlign="center">
        <Button primary onClick={() => resetSearch()}>
          {i18next.t("Start over")}
        </Button>
      </Segment>
    </ShouldRender>
  )
);

ExternalEmptyResultsElement.propTypes = {};

ExternalEmptyResultsElement.defaultProps = {};

export default ExternalEmptyResults;
