import * as React from "react";
import PropTypes from "prop-types";
import { Dimmer, Loader, Grid } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const OptionsLoadingSkeleton = ({ loadingMessage }) => (
  <Grid.Column stretched>
    <Dimmer active inverted>
      <Loader size="large" inline="centered" inverted>
        {loadingMessage}
      </Loader>
    </Dimmer>
  </Grid.Column>
);

OptionsLoadingSkeleton.propTypes = {
  loadingMessage: PropTypes.string,
};

OptionsLoadingSkeleton.defaultProps = {
  loadingMessage: i18next.t("Loading..."),
};

export default OptionsLoadingSkeleton;
