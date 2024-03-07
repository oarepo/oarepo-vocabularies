import React from "react";
import { Container, Grid } from "semantic-ui-react";
import { BaseFormLayout, useFormConfig } from "@js/oarepo_ui";
import { VocabularyFormSchema } from "./VocabularyFormSchema";
import { CurrentLocationInformation } from "./components";
import { useLocation } from "react-router-dom";
import _has from "lodash/has";

export const FormAppLayout = () => {
  const formikProps = {
    validationSchema: VocabularyFormSchema,
  };
  const { formConfig } = useFormConfig();

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");
  const editMode = _has(formConfig, "updateUrl");

  return (
    <Container fluid>
      <Grid>
        <Grid.Row className="rel-mb-2">
          <Grid.Column width={16}>
            <CurrentLocationInformation
              editMode={editMode}
              newChildItemParentId={newChildItemParentId}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>

      <BaseFormLayout formikProps={formikProps} />
    </Container>
  );
};
export default FormAppLayout;
