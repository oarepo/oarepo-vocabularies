import React from "react";
import { Message, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";

export const ErrorComponent = ({ error }) => {
  const { message } = error;
  return (
    <Message negative>
      <Icon name="warning" size="large" />
      {message}
    </Message>
  );
};

ErrorComponent.propTypes = {
  error: PropTypes.shape({
    status: PropTypes.number.isRequired,
    message: PropTypes.string.isRequired,
  }).isRequired,
};
