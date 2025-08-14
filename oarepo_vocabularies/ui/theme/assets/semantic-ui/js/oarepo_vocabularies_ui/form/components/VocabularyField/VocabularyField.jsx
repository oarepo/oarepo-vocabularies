import React, { forwardRef } from "react";
import PropTypes from "prop-types";
import { useFormConfig } from "@js/oarepo_ui/forms";
import { LocalVocabularySelectField } from "../LocalVocabularySelectField/LocalVocabularySelectField";
import { VocabularySelectField } from "../VocabularySelectField/VocabularySelectField";

export const VocabularyField = forwardRef(
  ({ fieldPath, vocabularyName, ...restProps }, ref) => {
    const { formConfig } = useFormConfig();
    const hasLocalOptions =
      formConfig?.vocabularies?.vocabularies?.[vocabularyName]?.all?.length > 0;
    const Field = hasLocalOptions
      ? LocalVocabularySelectField
      : VocabularySelectField;
    return (
      <Field
        fieldPath={fieldPath}
        vocabularyName={vocabularyName}
        ref={ref}
        {...restProps}
      />
    );
  }
);

VocabularyField.displayName = "VocabularyField";

VocabularyField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  vocabularyName: PropTypes.string.isRequired,
};
