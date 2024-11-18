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
        overriddenComponents={overriddenComponents}
        fieldPath={fieldPath}
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
};

VocabularyRemoteSelectField.defaultProps = {
  multiple: false,
  overriddenComponents: {},
  modalHeader: "",
};
