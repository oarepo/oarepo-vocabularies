import React, { useRef } from "react";
import PropTypes from "prop-types";
import { Container, Grid, Sticky, Ref } from "semantic-ui-react";
import { BaseForm, TextField } from "react-invenio-forms";
import {
  PublishButton,
  PropFieldsComponent,
  ResetButton,
  CurrentLocationInformation,
  VocabularyMultilingualInputField,
} from "./components";
import { useLocation } from "react-router-dom";
import { VocabularyFormSchema } from "./VocabularyFormSchema";
import Overridable from "react-overridable";
import { useFormConfig, FormFeedback, FormikStateLogger } from "@js/oarepo_ui";

export const DetailPageEditForm = ({
  initialValues,
  hasPropFields,
  editMode,
}) => {
  const {
    formConfig: { vocabularyProps },
  } = useFormConfig();

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");

  const sidebarRef = useRef(null);

  return (
    <Container>
      <BaseForm
        // onSubmit={onSubmit}
        formik={{
          initialValues: initialValues,
          validationSchema: VocabularyFormSchema,
          validateOnChange: false,
          validateOnBlur: false,
          enableReinitialize: true,
        }}
      >
        <Grid>
          <Grid.Row>
            <Grid.Column width={16}>
              <CurrentLocationInformation
                editMode={editMode}
                newChildItemParentId={newChildItemParentId}
              />
            </Grid.Column>
          </Grid.Row>

          <Grid.Column mobile={16} tablet={16} computer={12}>
            <VocabularyMultilingualInputField fieldPath="title" />
            <TextField fieldPath="id" label={"ID"} required />
            {hasPropFields && (
              <PropFieldsComponent vocabularyProps={vocabularyProps} />
            )}
            <FormFeedback />
            <FormikStateLogger />
          </Grid.Column>
          <Ref innerRef={sidebarRef}>
            <Grid.Column mobile={16} tablet={16} computer={4}>
              <Sticky context={sidebarRef} offset={20}>
                <Overridable id="FormApp.buttons">
                  <React.Fragment>
                    <PublishButton
                      newChildItemParentId={newChildItemParentId}
                    />
                    <ResetButton />
                  </React.Fragment>
                </Overridable>
              </Sticky>
            </Grid.Column>
          </Ref>
        </Grid>
      </BaseForm>
    </Container>
  );
};

DetailPageEditForm.propTypes = {
  initialValues: PropTypes.shape({
    title: PropTypes.object,
    ICO: PropTypes.string,
    RID: PropTypes.string,
    acronym: PropTypes.string,
    nameType: PropTypes.string,
  }),
  hasPropFields: PropTypes.bool,
};
