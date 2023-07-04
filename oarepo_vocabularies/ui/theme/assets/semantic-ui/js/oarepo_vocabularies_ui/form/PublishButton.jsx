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
        disabled={isSubmitting}
        loading={isSubmitting}
        color="green"
        onClick={handleSubmit}
      >
        {i18next.t("publish")}
      </Button>
    </Container>
  );
};

export const PublishButton = connect(PublishButtonComponent);

PublishButtonComponent.propTypes = {
  formik: PropTypes.object,
};
