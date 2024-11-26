import * as React from "react";
import PropTypes from "prop-types";
import { Dimmer, Loader } from "semantic-ui-react";

import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const OptionsLoadingSkeleton = ({ loading, loadingMessage }) =>
  loading && (
    <Dimmer active inverted>
      <Loader size="large" inline="centered" inverted>
        {loadingMessage}
      </Loader>
    </Dimmer>
  );

OptionsLoadingSkeleton.propTypes = {
  loading: PropTypes.bool,
  loadingMessage: PropTypes.string,
};

OptionsLoadingSkeleton.defaultProps = {
  loading: false,
  loadingMessage: i18next.t("Loading..."),
};

export default OptionsLoadingSkeleton;
