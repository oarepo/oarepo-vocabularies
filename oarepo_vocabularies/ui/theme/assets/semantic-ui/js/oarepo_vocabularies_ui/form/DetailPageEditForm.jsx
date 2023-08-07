import React, { useRef } from "react";
import PropTypes from "prop-types";
import { Container, Grid, Sticky, Ref } from "semantic-ui-react";
import { BaseForm, TextField } from "react-invenio-forms";
import {
  PublishButton,
  MultiLingualTextInput,
  PropFieldsComponent,
  ResetButton,
  CurrentLocationInformation,
} from "./components";
import { useLocation } from "react-router-dom";
import { VocabularyFormSchema } from "./VocabularyFormSchema";
import _omitBy from "lodash/omitBy";
import Overridable from "react-overridable";
import {
  useOnSubmit,
  useFormConfig,
  ErrorElement,
  RelatedSelectField,
  submitContextType,
} from "@js/oarepo_ui";

const removeNullAndUnderscoreProperties = (values, formik) => {
  return _omitBy(
    values,
    (value, key) =>
      value === null ||
      (Array.isArray(value) && value.every((item) => item === null)) ||
      key.startsWith("_")
  );
};

const setVocabularyHierarchy = (parentId) => {
  return (values, formik) => {
    if (parentId) values.hierarchy = { parent: parentId };
    return values
  };
};

export const DetailPageEditForm = ({
  initialValues,
  options,
  hasPropFields,
  editMode,
  apiCallUrl,
}) => {
  const {
    formConfig: { vocabularyProps },
  } = useFormConfig();

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");
  const currentPath = location.pathname;

  const { onSubmit, submitError } = useOnSubmit({
    apiUrl: apiCallUrl,
    context: editMode ? submitContextType.update : submitContextType.create,
    onBeforeSubmit: [
      setVocabularyHierarchy(newChildItemParentId),
      removeNullAndUnderscoreProperties,
    ],
    onSubmitSuccess: (result) => {
      window.location.href = editMode
        ? currentPath.replace("/edit", "")
        : currentPath.replace("_new", result.id)
    }
  });

  const sidebarRef = useRef(null);

  return (
    <Container>
      <BaseForm
        onSubmit={onSubmit}
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
            <MultiLingualTextInput fieldPath="title" options={options} />
            <TextField fieldPath="id" label={"ID"} width={11} required />
            {hasPropFields && (
              <PropFieldsComponent vocabularyProps={vocabularyProps} />
            )}
            {(submitError?.message) && (
              <ErrorElement error={submitError} />
            )}
          </Grid.Column>
          <Ref innerRef={sidebarRef}>
            <Grid.Column mobile={16} tablet={16} computer={4}>
              <Sticky context={sidebarRef} offset={20}>
                <Overridable id="FormApp.buttons">
                  <React.Fragment>
                    <PublishButton />
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

const TitlePropType = PropTypes.shape({
  language: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
});

DetailPageEditForm.propTypes = {
  initialValues: PropTypes.shape({
    title: PropTypes.object,
    ICO: PropTypes.string,
    RID: PropTypes.string,
    acronym: PropTypes.string,
    nameType: PropTypes.string,
  }),
  hasPropFields: PropTypes.bool,
  options: PropTypes.shape({
    languages: PropTypes.arrayOf(
      PropTypes.shape({
        text: PropTypes.string.isRequired,
        value: PropTypes.string.isRequired,
      })
    ),
  }),
};
