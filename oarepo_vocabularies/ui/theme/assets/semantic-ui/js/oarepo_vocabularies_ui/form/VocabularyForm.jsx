import React from "react";
import PropTypes from "prop-types";
import { DetailPageEditForm } from "./DetailPageEditForm";
import { translateObjectToArray, clearObjectValues } from "../utils";
import _ from "lodash";
import { useFormConfig } from "@js/oarepo_ui/forms";

const options = {
  languages: [
    { text: "cs", value: "cs" },
    { text: "en", value: "en" },
    { text: "de", value: "de" },
  ],
};

const VocabularyForm = () => {
  const { record, formConfig } = useFormConfig();
  const { vocabularyProps } = formConfig;
  const editMode = _.has(formConfig, "updateUrl");
  const hasPropFields = !_.isEmpty(vocabularyProps);
  const apiCallUrl = editMode ? formConfig.updateUrl : formConfig.createUrl;
  console.log(record);
  const availablePropFields = clearObjectValues(vocabularyProps.props);

  const editModeAndProps = editMode
    ? { ...availablePropFields, ...record.props }
    : availablePropFields;

  const propFieldsWithValues = hasPropFields ? editModeAndProps : {};

  const initialValues = editMode
    ? {
        title: translateObjectToArray(record.title),
        props: propFieldsWithValues,
        id: record.id,
      }
    : {
        title: [{ language: "cs", title: "" }],
        props: propFieldsWithValues,
        id: "",
      };

  return (
    <DetailPageEditForm
      initialValues={initialValues}
      formConfig={formConfig}
      options={options}
      hasPropFields={hasPropFields}
      vocabularyProps={vocabularyProps}
      apiCallUrl={apiCallUrl}
      editMode={editMode}
      record={record}
    />
  );
};

VocabularyForm.propTypes = {
  record: PropTypes.object.isRequired,
  formConfig: PropTypes.object.isRequired,
};

export default VocabularyForm;
