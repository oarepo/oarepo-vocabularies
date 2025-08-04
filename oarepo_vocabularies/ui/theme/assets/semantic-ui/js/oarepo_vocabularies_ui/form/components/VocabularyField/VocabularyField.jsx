import React from "react";
import PropTypes from "prop-types";
import { useFormConfig } from "@js/oarepo_ui/forms";
import { LocalVocabularySelectField } from "../LocalVocabularySelectField/LocalVocabularySelectField";
import { VocabularySelectField } from "../VocabularySelectField/VocabularySelectField";

/**
 * VocabularyField: Combines LocalVocabularySelectField and VocabularySelectField.
 * If options for vocabularyName are present in formConfig, uses LocalVocabularySelectField.
 * Otherwise, falls back to VocabularySelectField.
 * Always requires fieldPath and vocabularyName, passes rest props to the chosen field.
 */
export const VocabularyField = ({
  fieldPath,
  vocabularyName,
  ...restProps
}) => {
  const { formConfig } = useFormConfig();
  const vocabularies = formConfig?.vocabularies || {};
  const hasLocalOptions = vocabularies?.[vocabularyName]?.all?.length > 0;
  console.log(vocabularyName);
  if (hasLocalOptions) {
    return (
      <LocalVocabularySelectField
        fieldPath={fieldPath}
        vocabularyName={vocabularyName}
        {...restProps}
      />
    );
  } else {
    return (
      <VocabularySelectField
        fieldPath={fieldPath}
        vocabularyName={vocabularyName}
        {...restProps}
      />
    );
  }
};

VocabularyField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  vocabularyName: PropTypes.string.isRequired,
};
