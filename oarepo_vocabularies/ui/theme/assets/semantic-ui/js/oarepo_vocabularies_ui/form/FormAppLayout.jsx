import React from "react";
import { Container } from "semantic-ui-react";
import { BaseFormLayout } from "@js/oarepo_ui";
import { VocabularyFormSchema } from "./VocabularyFormSchema";

export const FormAppLayout = () => {
  const formikProps = {
    validationSchema: VocabularyFormSchema,
  };
  return (
    <Container fluid>
      <BaseFormLayout formikProps={formikProps} />
    </Container>
  );
};
export default FormAppLayout;
