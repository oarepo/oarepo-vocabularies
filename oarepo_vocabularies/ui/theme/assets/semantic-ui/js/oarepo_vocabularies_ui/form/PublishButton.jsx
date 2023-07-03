import React from "react";
import { connect } from "formik";
import { Button } from "semantic-ui-react";
import PropTypes from "prop-types";

const PublishButtonComponent = ({ formik }) => {
  const { handleSubmit } = formik;
  return <Button onClick={handleSubmit}>Publish</Button>;
};

export const PublishButton = connect(PublishButtonComponent);

PublishButtonComponent.propTypes = {
  formik: PropTypes.object,
};
