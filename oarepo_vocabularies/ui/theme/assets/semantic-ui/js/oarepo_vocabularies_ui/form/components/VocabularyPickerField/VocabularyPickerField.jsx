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

export const VocabularyPickerField = ({
  fieldPath,
  multiple,
  label,
  helpText,
  initialValue,
  className,
  required,
  children,
  ...uiProps
}) => {
  const { values, setFieldValue } = useFormikContext();
  const _initialValue = initialValue ?? multiple ? [] : {};
  const fieldValue = getIn(values, fieldPath, _initialValue);

  // Ignore any invalid field values
  const validatedValue = multiple
    ? fieldValue.filter((val) => val.id)
    : fieldValue.id
    ? fieldValue
    : {};

  const addValue = (item) => {
    if (!multiple) {
      setFieldValue(fieldPath, item);
    } else {
      const newValue = [...validatedValue, item];
      setFieldValue(fieldPath, newValue);
    }
  };

  const removeValue = (item) => {
    if (!multiple) {
      setFieldValue(fieldPath, {});
    } else {
      const newValue = [...validatedValue];
      _remove(newValue, (value) => value.id === item.id);
      setFieldValue(fieldPath, newValue);
    }
  };

  return (
    <Form.Field
      className={`vocabulary picker ${className}`}
      required={required}
      {...uiProps}
    >
      <FieldValueProvider
        value={{ value: validatedValue, multiple, addValue, removeValue }}
      >
        {label}
        <label className="helptext">{helpText}</label>
        {!_isEmpty(validatedValue) && (
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

VocabularyPickerField.propTypes = {};

VocabularyPickerField.defaultProps = {};

export default VocabularyPickerField;
