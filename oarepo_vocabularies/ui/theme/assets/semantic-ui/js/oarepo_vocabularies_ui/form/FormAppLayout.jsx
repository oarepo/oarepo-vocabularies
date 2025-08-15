import React from "react";
import { Container, Grid } from "semantic-ui-react";
import { BaseFormLayout, useFormConfig } from "@js/oarepo_ui/forms";
import { CurrentLocationInformation } from "./components";
import { useLocation } from "react-router-dom";
import _has from "lodash/has";

export const FormAppLayout = () => {
  const { formConfig } = useFormConfig();

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");
  const isUpdateForm = _has(formConfig, "updateUrl");

  return (
    <Container fluid>
      <Grid>
        <Grid.Row className="rel-mb-2">
          <Grid.Column width={16}>
            <CurrentLocationInformation
              isUpdateForm={isUpdateForm}
              newChildItemParentId={newChildItemParentId}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>

      <BaseFormLayout formikProps={{}} />
    </Container>
  );
};
export default FormAppLayout;
