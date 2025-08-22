import React from "react";
import { Message } from "semantic-ui-react";
import PropTypes from "prop-types";

export const VocabularyBreadcrumbMessage = ({
  icon = "attention",
  header,
  size = "tiny",
  content,
}) => {
  return <Message icon={icon} header={header} size={size} content={content} />;
};

/* eslint-disable react/require-default-props */
VocabularyBreadcrumbMessage.propTypes = {
  icon: PropTypes.string,
  header: PropTypes.string.isRequired,
  size: PropTypes.string,
  content: PropTypes.oneOfType([PropTypes.node, PropTypes.string]).isRequired,
};
/* eslint-enable react/require-default-props */
