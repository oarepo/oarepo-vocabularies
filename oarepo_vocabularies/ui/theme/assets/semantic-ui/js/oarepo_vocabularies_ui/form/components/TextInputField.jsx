// component that wraps invenio-form's TextField. The reason for this component is
// because when making new item, you get null values as part of record and this
//causes multiple issues
// 1st you get error that input value must not be null
//2nd when you start typing in that field you get error message that you are changing
// uncontrolled input to controlled. Not sure if this could be also managed on BE side
// in which case such a component would not be required and we can use Invenio's directly

import React from "react";
import { TextField } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";
import PropTypes from "prop-types";

export const TextInputField = ({
  fieldPath,
  label,
  width,
  required,
  error,
}) => {
  const { values } = useFormikContext();

  return (
    <TextField
      value={!getIn(values, fieldPath) ? "" : getIn(values, fieldPath)}
      fieldPath={fieldPath}
      label={label}
      width={width}
      required={required}
    />
  );
};

TextInputField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  error: PropTypes.any,
  helpText: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  disabled: PropTypes.bool,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]).isRequired,
  optimized: PropTypes.bool,
  required: PropTypes.bool,
};

TextInputField.defaultProps = {
  error: undefined,
  helpText: "",
  disabled: false,
  optimized: false,
  required: false,
};
