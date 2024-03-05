import React, { useRef } from "react";
import PropTypes from "prop-types";
import { Container, Grid, Sticky, Ref, Card } from "semantic-ui-react";
import {
  TextField,
  MultiInput,
  CustomFields,
  FieldLabel,
} from "react-invenio-forms";
import {
  PublishButton,
  PropFieldsComponent,
  ResetButton,
  FeaturedButton,
  CurrentLocationInformation,
  VocabularyMultilingualInputField,
} from "./components";
import { useLocation } from "react-router-dom";
import { VocabularyFormSchema } from "./VocabularyFormSchema";
import Overridable from "react-overridable";
import { useFormConfig, FormFeedback, BaseForm } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _isEmpty from "lodash/isEmpty";

export const DetailPageEditForm = ({
  initialValues,
  hasPropFields,
  editMode,
}) => {
  const {
    formConfig: { vocabularyProps, custom_fields: customFields },
  } = useFormConfig();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");
  const sidebarRef = useRef(null);

  return (
    <Container>
      <BaseForm
        onSubmit={() => {}}
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

          <Grid.Column id="main-content" mobile={16} tablet={16} computer={11}>
            <VocabularyMultilingualInputField
              fieldPath="title"
              textFieldLabel={i18next.t("Title")}
              labelIcon="pencil"
            />
            <TextField
              fieldPath="id"
              label={
                <FieldLabel
                  htmlFor="id"
                  icon="pencil"
                  label={i18next.t("ID")}
                />
              }
              required
            />
            <MultiInput
              fieldPath="tags"
              label={i18next.t("Tags")}
              icon="tags"
              placeholder={i18next.t("Enter one or more tags.")}
              required={false}
            />
            {hasPropFields && (
              <PropFieldsComponent vocabularyProps={vocabularyProps} />
            )}
            {!_isEmpty(customFields.ui) && (
              <CustomFields
                config={customFields.ui[initialValues?.type]}
                templateLoaders={[
                  (widget) => import(`@templates/custom_fields/${widget}.js`),
                  (widget) => import(`react-invenio-forms`),
                ]}
                fieldPathPrefix="custom_fields"
              />
            )}
            <FormFeedback />
          </Grid.Column>
          <Ref innerRef={sidebarRef} className="rel-mt-3">
            <Grid.Column
              id="control-panel"
              mobile={16}
              tablet={16}
              computer={5}
            >
              <Sticky context={sidebarRef} offset={20}>
                <Overridable id="FormApp.buttons">
                  <Card fluid>
                    <Card.Content>
                      <Grid>
                        <Grid.Column width={16}>
                          <PublishButton
                            newChildItemParentId={newChildItemParentId}
                          />
                        </Grid.Column>
                        <Grid.Column width={16}>
                          <FeaturedButton
                            fluid
                            color="green"
                            icon="upload"
                            labelPosition="left"
                            type="button"
                          />
                        </Grid.Column>
                        <Grid.Column width={16}>
                          <ResetButton />
                        </Grid.Column>
                      </Grid>
                    </Card.Content>
                  </Card>
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
    type: PropTypes.string,
  }),
  hasPropFields: PropTypes.bool,
  editMode: PropTypes.bool,
};
