import React from "react";
import { connect } from "formik";
import { Button, Container } from "semantic-ui-react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

const PublishButtonComponent = ({ formik }) => {
  const { handleSubmit, isSubmitting } = formik;
  return (
    <Container textAlign="center">
      <Button
        fluid
        disabled={isSubmitting}
        loading={isSubmitting}
        color="green"
        onClick={handleSubmit}
        icon="upload"
        labelPosition="left"
        content={i18next.t("publish")}
        type="button"
      />
    </Container>
  );
};

export const PublishButton = connect(PublishButtonComponent);

PublishButtonComponent.propTypes = {
  formik: PropTypes.object,
};
