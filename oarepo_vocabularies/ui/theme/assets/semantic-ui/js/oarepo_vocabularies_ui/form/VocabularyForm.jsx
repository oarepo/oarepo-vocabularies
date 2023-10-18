import React from "react";
import { DetailPageEditForm } from "./DetailPageEditForm";
import _has from "lodash/has";
import { useFormConfig } from "@js/oarepo_ui/forms";

const VocabularyForm = () => {
  const { record, formConfig } = useFormConfig();
  const { vocabularyProps } = formConfig;
  const editMode = _has(formConfig, "updateUrl");
  const hasPropFields = _has(vocabularyProps, "props");

  return (
    <DetailPageEditForm
      initialValues={record}
      hasPropFields={hasPropFields}
      editMode={editMode}
    />
  );
};

export default VocabularyForm;
