import React from "react";
import PropTypes from "prop-types";
import { VocabularyRemoteSelectModal } from "./VocabularyRemoteSelectModal";
import { VocabularyPickerField } from "../VocabularyPickerField";

export const VocabularyRemoteSelectField = ({
  vocabulary,
  fieldPath,
  label,
  helpText,
  multiple = false,
  required,
  triggerButton,
  triggerLabel,
  overriddenComponents = {},
  modalHeader = "",
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
        triggerLabel={triggerLabel}
        label={modalHeader}
        overriddenComponents={overriddenComponents}
        fieldPath={fieldPath}
        {...restProps}
      />
    </VocabularyPickerField>
  );
};

/* eslint-disable react/require-default-props */
VocabularyRemoteSelectField.propTypes = {
  vocabulary: PropTypes.string.isRequired,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  helpText: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  modalHeader: PropTypes.string,
  multiple: PropTypes.bool,
  required: PropTypes.bool,
  triggerButton: PropTypes.node,
  triggerLabel: PropTypes.string,
  overriddenComponents: PropTypes.object,
};
/* eslint-enable react/require-default-props */
