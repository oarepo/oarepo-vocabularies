import React from "react";

import _join from "lodash/join";
import PropTypes from "prop-types";
import { getIn, useFormikContext } from "formik";
import { Form } from "semantic-ui-react";
import { VocabularyRemoteSelectModal } from "./VocabularyRemoteSelectModal";
import { useFieldData } from "@js/oarepo_ui";

export const VocabularyRemoteSelectField = ({
  vocabulary,
  fieldPath,
  label,
  helpText,
  multiple,
  required,
  ...restProps
}) => {
  const { getFieldData } = useFieldData();
  const { values, setFieldValue } = useFormikContext();

  const {
    label: modelLabel,
    helpText: modelHelpText,
    required: modelRequired,
  } = getFieldData({ fieldPath, icon: "drivers license" });

  const value = getIn(values, fieldPath, {})?.id
    ? getIn(values, fieldPath, {})
    : "";

  const onChange = (value) => {
    setFieldValue(fieldPath, value);
  };

  return (
    <Form.Field required={required ?? modelRequired}>
      {label ?? modelLabel}
      <label className="helptext">{helpText ?? modelHelpText}</label>
      <VocabularyRemoteSelectModal
        vocabulary={vocabulary}
        value={value}
        onChange={onChange}
        {...restProps}
      />
    </Form.Field>
  );
};

VocabularyRemoteSelectField.propTypes = {
  // type: PropTypes.string.isRequired,
  // fieldPath: PropTypes.string.isRequired,
  externalAuthority: PropTypes.bool,
  multiple: PropTypes.bool,
  triggerButtonLabel: PropTypes.string,
  helpText: PropTypes.string,
  label: PropTypes.string,
  fieldPath: PropTypes.string.isRequired,
  vocabulary: PropTypes.string.isRequired,
};

VocabularyRemoteSelectField.defaultProps = {
  multiple: false,
  externalAuthority: false,
};
