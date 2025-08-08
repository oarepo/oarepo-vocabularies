import React from "react";
import PropTypes from "prop-types";
import { useFormConfig } from "@js/oarepo_ui/forms";
import { LocalVocabularySelectField } from "../LocalVocabularySelectField/LocalVocabularySelectField";
import { VocabularySelectField } from "../VocabularySelectField/VocabularySelectField";

export const VocabularyField = ({
  fieldPath,
  vocabularyName,
  filterFunction = undefined,
  ref,
  showLeafsOnly = false,
  ...restProps
}) => {
  const { formConfig } = useFormConfig();
  const vocabularies = formConfig?.vocabularies || {};
  const hasLocalOptions = vocabularies?.[vocabularyName]?.all?.length > 0;
  if (hasLocalOptions) {
    return (
      <LocalVocabularySelectField
        fieldPath={fieldPath}
        vocabularyName={vocabularyName}
        filterFunction={filterFunction}
        ref={ref}
        showLeafsOnly={showLeafsOnly}
        {...restProps}
      />
    );
  } else {
    return (
      <VocabularySelectField
        fieldPath={fieldPath}
        vocabularyName={vocabularyName}
        filterFunction={filterFunction}
        ref={ref}
        showLeafsOnly={showLeafsOnly}
        {...restProps}
      />
    );
  }
};

VocabularyField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  vocabularyName: PropTypes.string.isRequired,
  showLeafsOnly: PropTypes.bool,
  filterFunction: PropTypes.func,
};
