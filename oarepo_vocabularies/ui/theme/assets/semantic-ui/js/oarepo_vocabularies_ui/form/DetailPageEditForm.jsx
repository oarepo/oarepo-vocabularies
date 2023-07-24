import React, { useRef } from "react";
import PropTypes from "prop-types";
import { Container, Grid, Sticky, Ref } from "semantic-ui-react";
import { BaseForm } from "react-invenio-forms";
import { PublishButton } from "./components/PublishButton";
import { MultiLingualTextInput } from "./components/MultiLingualTextInput";
import { PropFieldsComponent } from "./components/PropFieldsComponent";
import { extractVariablePart } from "../utils";
import { useLocation } from "react-router-dom";
import { ErrorComponent } from "./components/Error";
import { ResetButton } from "./components/ResetButton";
import { VocabularyFormSchema } from "./VocabularyFormSchema";
import { FormikStateLogger } from "./components/FormikStateLogger";
import { CurrentLocationInformation } from "./components/CurrentLocationInformation";
import { useFormConfig } from "@js/oarepo_ui/forms";
import _omitBy from "lodash/omitBy";
import Overridable from "react-overridable";
import { VocabulariesApiClientInitialized } from "./api/DepositApiClient";
import { TextInputField } from "./components/TextInputField";
import { useMutation } from "@tanstack/react-query";

const removeNullAndUnderscoreProperties = (obj) => {
  return _omitBy(
    obj,
    (value, key) =>
      value === null ||
      (Array.isArray(value) && value.every((item) => item === null)) ||
      key.startsWith("_") ||
      key === "pids" ||
      key === "files"
  );
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
  const sidebarRef = useRef(null);
  const location = useLocation();
  const currentPath = location.pathname;
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");
  console.log(apiCallUrl);
  const { error: saveError, mutateAsync: saveMutateAsync } = useMutation({
    mutationFn: async ({ apiCallUrl, editedItem }) =>
      VocabulariesApiClientInitialized.saveDraft(apiCallUrl, editedItem),
  });
  const { error: createError, mutateAsync: createMutateAsync } = useMutation({
    mutationFn: async ({ apiCallUrl, newItem }) =>
      VocabulariesApiClientInitialized.createDraft(apiCallUrl, newItem),
  });

  const onSubmit = (values, formik) => {
    let preparedValues = values;
    if (newChildItemParentId)
      preparedValues.hierarchy = { parent: newChildItemParentId };

    if (editMode) {
      saveMutateAsync({
        apiCallUrl,
        editedItem: removeNullAndUnderscoreProperties(preparedValues),
      })
        .then(() => {
          formik.setSubmitting(false);
          window.location.href = currentPath.replace("/edit", "");
        })
        .catch((error) => {
          formik.setSubmitting(false);
        });
    } else {
      createMutateAsync({
        apiCallUrl,
        newItem: removeNullAndUnderscoreProperties(preparedValues),
      })
        .then((response) => {
          formik.setSubmitting(false);
          window.location.href = currentPath.replace("_new", values.id);
        })
        .catch((error) => {
          formik.setSubmitting(false);
        });
    }
  };

  return (
    <Container>
      <BaseForm
        onSubmit={onSubmit}
        // onError={this.onError}
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
            <TextInputField fieldPath="id" label={"ID"} width={11} required />
            {hasPropFields && (
              <PropFieldsComponent vocabularyProps={vocabularyProps} />
            )}
            <FormikStateLogger />
            {(saveError?.message || createError?.message) && (
              <ErrorComponent error={saveError || createError} />
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
  vocabularyProps: PropTypes.object,
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
