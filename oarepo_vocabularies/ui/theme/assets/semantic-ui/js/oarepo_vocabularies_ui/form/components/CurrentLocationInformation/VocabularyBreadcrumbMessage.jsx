import React from "react";
import { Message } from "semantic-ui-react";
import PropTypes from "prop-types";

export const VocabularyBreadcrumbMessage = ({
  icon,
  header,
  size,
  content,
}) => {
  return <Message icon={icon} header={header} size={size} content={content} />;
};

VocabularyBreadcrumbMessage.propTypes = {
  icon: PropTypes.string,
  header: PropTypes.string.isRequired,
  size: PropTypes.string,
  content: PropTypes.oneOfType([PropTypes.node, PropTypes.string]),
};

VocabularyBreadcrumbMessage.defaultProps = {
  icon: "attention",
  size: "tiny",
};
