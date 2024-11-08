import React from "react";
import PropTypes from "prop-types";
import { VocabularyRemoteSelectModal } from "./VocabularyRemoteSelectModal";
import { VocabularyPickerField } from "../VocabularyPickerField";

export const VocabularyRemoteSelectField = ({
  vocabulary,
  fieldPath,
  label,
  helpText,
  multiple,
  required,
  triggerButton,
  overriddenComponents,
  modalHeader,
  allowInlineVocabularyItemCreation,
  vocabularyItemCreationFormUrl,
  ...restProps
}) => {
  return (
    <VocabularyPickerField
      className="remote select"
      fieldPath={fieldPath}
      label={label}
      helpText={helpText}
      multiple={multiple}
      required={required}
    >
      <VocabularyRemoteSelectModal
        vocabulary={vocabulary}
        trigger={triggerButton}
        label={modalHeader}
        // overriddenComponents={overriddenComponents}
        allowInlineVocabularyItemCreation={allowInlineVocabularyItemCreation}
        vocabularyItemCreationFormUrl={vocabularyItemCreationFormUrl}
        {...restProps}
      />
    </VocabularyPickerField>
  );
};

VocabularyRemoteSelectField.propTypes = {
  vocabulary: PropTypes.string.isRequired,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  helpText: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  modalHeader: PropTypes.string,
  multiple: PropTypes.bool,
  required: PropTypes.bool,
  triggerButton: PropTypes.node,
  overriddenComponents: PropTypes.object,
  allowInlineVocabularyItemCreation: PropTypes.bool,
  vocabularyItemCreationFormUrl: PropTypes.string,
};

VocabularyRemoteSelectField.defaultProps = {
  multiple: false,
  overriddenComponents: undefined,
  modalHeader: "",
  // must be explicitly provided by user of cmp and appropriate component must
  // exist on the BE to allow for creation of new vocabulary items directly
  // from deposit form
  allowInlineVocabularyItemCreation: true,
  vocabularyItemCreationFormUrl: undefined,
};
