import React from "react";
import { connect } from "formik";
import { Button, Container } from "semantic-ui-react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

const ResetButtonComponent = ({ formik }) => {
  const { handleReset } = formik;
  return (
    <Container className="mt-5" textAlign="center">
      <Button
        fluid
        color="red"
        onClick={handleReset}
        content={i18next.t("reset")}
        icon="times rectangle"
        labelPosition="left"
      />
    </Container>
  );
};

export const ResetButton = connect(ResetButtonComponent);

ResetButtonComponent.propTypes = {
  formik: PropTypes.object,
};
