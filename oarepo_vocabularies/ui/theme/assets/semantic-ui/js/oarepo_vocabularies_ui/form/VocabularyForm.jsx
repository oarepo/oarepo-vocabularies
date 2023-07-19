import React from "react";
import { DetailPageEditForm } from "./DetailPageEditForm";
import { translateObjectToArray } from "../utils";
import _has from "lodash/has";
import _isEmpty from "lodash/isEmpty";
import _mapValues from "lodash/mapValues";
import { useFormConfig } from "@js/oarepo_ui/forms";

const options = {
  languages: [
    { text: "cs", value: "cs" },
    { text: "en", value: "en" },
    { text: "de", value: "de" },
  ],
};

const VocabularyForm = () => {
  const { record, formConfig, recordPermissions } = useFormConfig();
  console.log(record, formConfig, recordPermissions);
  const { vocabularyProps } = formConfig;
  const editMode = _has(formConfig, "updateUrl");
  const hasPropFields = !_isEmpty(vocabularyProps);
  const apiCallUrl = editMode ? formConfig.updateUrl : formConfig.createUrl;
  const availablePropFields = _mapValues(vocabularyProps.props, () => "");
  console.log(availablePropFields);
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

export default VocabularyForm;
