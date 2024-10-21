import * as React from "react";
import PropTypes from "prop-types";
import { withState } from "react-searchkit";
import { Dimmer, Loader } from "semantic-ui-react";

import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const OptionsLoadingSkeleton = withState(
  ({ currentResultsState: results, loadingMessage }) =>
    results.loading && (
      <Dimmer active inverted>
        <Loader size="large" inline="centered" inverted>
          {loadingMessage}
        </Loader>
      </Dimmer>
    )
);

OptionsLoadingSkeleton.propTypes = {
  loadingMessage: PropTypes.string,
};

OptionsLoadingSkeleton.defaultProps = {
  loadingMessage: i18next.t("Loading..."),
};

export default OptionsLoadingSkeleton;
