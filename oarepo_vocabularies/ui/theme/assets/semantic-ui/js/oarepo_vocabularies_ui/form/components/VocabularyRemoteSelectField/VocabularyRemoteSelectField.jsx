import React from "react";

import PropTypes from "prop-types";
import { getIn, useFormikContext } from "formik";
import { Form, Grid } from "semantic-ui-react";
import { VocabularyRemoteSelectModal } from "./VocabularyRemoteSelectModal";
import {
  VocabularyRemoteSelectValue,
  VocabularyRemoteSelectValues,
} from "./VocabularyRemoteSelectValues";
import { useFieldData } from "@js/oarepo_ui";
import _isEmpty from "lodash/isEmpty";
import _remove from "lodash/remove";
import { FieldValueProvider } from "./context";

export const VocabularyRemoteSelectField = ({
  vocabulary,
  fieldPath,
  label,
  helpText,
  multiple,
  required,
  triggerButton,
  overriddenComponents,
  ...restProps
}) => {
  const { getFieldData } = useFieldData();
  const { values, setFieldValue } = useFormikContext();

  const {
    label: modelLabel,
    helpText: modelHelpText,
    required: modelRequired,
  } = getFieldData({ fieldPath, icon: "drivers license" });

  const initialValue = multiple ? [] : {};
  const fieldValue = getIn(values, fieldPath, initialValue);

  const addItem = React.useCallback((item) => {
    if (!multiple) {
      setFieldValue(fieldPath, item);
    } else {
      const newValue = [...fieldValue, item];
      setFieldValue(fieldPath, newValue);
    }
  });

  const removeItem = React.useCallback((item) => {
    if (!multiple) {
      setFieldValue(fieldPath, initialValue);
    } else {
      const newValue = [...fieldValue];
      _remove(newValue, (value) => value.id === item.id);
      setFieldValue(fieldPath, newValue);
    }
  });

  return (
    <Form.Field
      className="vocabulary select remote"
      required={required ?? modelRequired}
    >
      <FieldValueProvider value={{ value: fieldValue, multiple }}>
        {label ?? modelLabel}
        <label className="helptext">{helpText ?? modelHelpText}</label>
        {!_isEmpty(fieldValue) && (
          <Grid.Row className="rel-mb-1">
            {(multiple && (
              <VocabularyRemoteSelectValues removeItem={removeItem} />
            )) || (
              <VocabularyRemoteSelectValue
                value={fieldValue}
                removeItem={removeItem}
              />
            )}
          </Grid.Row>
        )}
        <VocabularyRemoteSelectModal
          vocabulary={vocabulary}
          addItem={addItem}
          removeItem={removeItem}
          trigger={triggerButton}
          label={
            label ??
            getFieldData({ fieldPath, fieldRepresentation: "text" }).label
          }
          {...restProps}
        />
      </FieldValueProvider>
    </Form.Field>
  );
};

VocabularyRemoteSelectField.propTypes = {
  vocabulary: PropTypes.string.isRequired,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  helpText: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  multiple: PropTypes.bool,
  required: PropTypes.bool,
  triggerButton: PropTypes.node,
  overriddenComponents: PropTypes.object,
};

VocabularyRemoteSelectField.defaultProps = {
  multiple: false,
  overriddenComponents: {},
};
