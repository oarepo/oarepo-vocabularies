import React from "react";
import { DetailPageEditForm } from "./DetailPageEditForm";
import _has from "lodash/has";
import _isEmpty from "lodash/isEmpty";
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

  return (
    <DetailPageEditForm
      initialValues={record}
      formConfig={formConfig}
      options={options}
      hasPropFields={hasPropFields}
      vocabularyProps={vocabularyProps}
      apiCallUrl={apiCallUrl}
      editMode={editMode}
    />
  );
};

export default VocabularyForm;
