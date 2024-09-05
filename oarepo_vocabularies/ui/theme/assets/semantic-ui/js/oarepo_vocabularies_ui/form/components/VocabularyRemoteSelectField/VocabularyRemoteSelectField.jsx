import React from "react";

import _join from "lodash/join";
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

  const initialValue = multiple ? [] : {};
  const fieldValue = getIn(values, fieldPath, initialValue);

  const addItem = React.useCallback((item) => {
    if (!multiple) {
      setFieldValue(fieldPath, item);
    } else {
      const newValue = [...fieldValue.push(item)];
      setFieldValue(fieldPath, newValue);
    }
  });

  const removeItem = React.useCallback((item) => {
    setFieldValue(fieldPath, initialValue);
  });

  const onChange = React.useCallback((value) => {}, [fieldPath]);

  return (
    <Form.Field required={required ?? modelRequired}>
      {label ?? modelLabel}
      <label className="helptext">{helpText ?? modelHelpText}</label>
      {!_isEmpty(fieldValue) && (
        <Grid.Row className="rel-mb-1">
          {(multiple && (
            <VocabularyRemoteSelectValues
              fieldValue={fieldValue}
              removeItem={removeItem}
            />
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
        value={fieldValue}
        addItem={addItem}
        removeItem={removeItem}
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
