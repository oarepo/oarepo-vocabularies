import React from "react";
import { withState } from "react-searchkit";
import { Header, Container } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { ShouldRender } from "@js/oarepo_ui/search";
import { SearchSource } from "./constants";
import { featuredFilterActive } from "./util";

export const VocabularyRemoteFeaturedResults = withState(
  ({ currentQueryState, currentResultsState: results, source }) => {
    const filterActive = featuredFilterActive(currentQueryState);

    return (
      <ShouldRender
        condition={
          currentQueryState.queryString === "" &&
          (!currentQueryState.suggestionString ||
            currentQueryState.suggestionString === "") &&
          source === SearchSource.INTERNAL &&
          filterActive &&
          results.data.total > 0
        }
      >
        <Container>
          <Header disabled className="primary" sub>
            {i18next.t("Frequently used")}
          </Header>
        </Container>
      </ShouldRender>
    );
  }
);

VocabularyRemoteFeaturedResults.propTypes = {};

export default VocabularyRemoteFeaturedResults;
