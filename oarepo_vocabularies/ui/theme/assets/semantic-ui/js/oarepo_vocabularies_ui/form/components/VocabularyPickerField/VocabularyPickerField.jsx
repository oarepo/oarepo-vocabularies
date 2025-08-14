import * as React from "react";
import PropTypes from "prop-types";
import { getIn, useFormikContext } from "formik";
import _isEmpty from "lodash/isEmpty";
import _remove from "lodash/remove";
import { Form, Grid } from "semantic-ui-react";
import { FieldValueProvider } from "../VocabularyRemoteSelectField/context";
import {
  SelectedVocabularyValue,
  SelectedVocabularyValues,
} from "../SelectedVocabularyValues";

const sanitizeValue = (multiple, value) => {
  if (multiple) {
    return value.filter((val) => val.id);
  } else {
    return value.id ? value : {};
  }
};

export const VocabularyPickerField = ({
  fieldPath,
  multiple,
  label,
  helpText,
  initialValue,
  className,
  required,
  children,
  onChange = () => {},
  ...uiProps
}) => {
  const { values, setFieldValue } = useFormikContext();
  const _initialValue = initialValue ?? multiple ? [] : {};
  const fieldValue = getIn(values, fieldPath, _initialValue);

  // Ignore any invalid field values
  const sanitizedValue = sanitizeValue(multiple, fieldValue);

  const addValue = (item) => {
    if (!multiple) {
      setFieldValue(fieldPath, item, true);
    } else {
      const newValue = [...sanitizedValue, item];
      setFieldValue(fieldPath, newValue, true);
      onChange(newValue);
    }
  };

  const removeValue = (item) => {
    if (!multiple) {
      setFieldValue(fieldPath, {});
    } else {
      const newValue = [...sanitizedValue];
      _remove(newValue, (value) => value.id === item.id);
      setFieldValue(fieldPath, newValue, true);
      onChange(newValue);
    }
  };

  return (
    <Form.Field
      className={`vocabulary picker ${className}`}
      required={required}
      {...uiProps}
    >
      <FieldValueProvider
        value={{ value: sanitizedValue, multiple, addValue, removeValue }}
      >
        {label}
        <label className="helptext">{helpText}</label>
        {!_isEmpty(sanitizedValue) && (
          <Grid.Row className="rel-mb-1">
            {(multiple && <SelectedVocabularyValues />) || (
              <SelectedVocabularyValue />
            )}
          </Grid.Row>
        )}
        {children}
      </FieldValueProvider>
    </Form.Field>
  );
};

/* eslint-disable react/require-default-props */
VocabularyPickerField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  helpText: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  multiple: PropTypes.bool,
  required: PropTypes.bool,
  initialValue: PropTypes.oneOfType([PropTypes.array, PropTypes.object]),
  className: PropTypes.string,
  children: PropTypes.node,
  onChange: PropTypes.func,
};
/* eslint-enable react/require-default-props */

VocabularyPickerField.defaultProps = {};

export default VocabularyPickerField;
