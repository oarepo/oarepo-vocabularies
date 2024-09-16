import React from "react";

import PropTypes from "prop-types";
import { getIn, useFormikContext } from "formik";
import { Form, Grid } from "semantic-ui-react";
import { VocabularyRemoteSelectModal } from "./VocabularyRemoteSelectModal";
import {
  VocabularyRemoteSelectValue,
  VocabularyRemoteSelectValues,
} from "./VocabularyRemoteSelectValues";
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
  modalHeader,
  ...restProps
}) => {
  const { values, setFieldValue } = useFormikContext();

  const initialValue = multiple ? [] : {};
  const fieldValue = getIn(values, fieldPath, initialValue);

  const addValue = React.useCallback((item) => {
    if (!multiple) {
      setFieldValue(fieldPath, item);
    } else {
      const newValue = [...fieldValue, item];
      setFieldValue(fieldPath, newValue);
    }
  });

  const removeValue = React.useCallback((item) => {
    if (!multiple) {
      setFieldValue(fieldPath, null);
    } else {
      const newValue = [...fieldValue];
      _remove(newValue, (value) => value.id === item.id);
      setFieldValue(fieldPath, newValue);
    }
  });

  return (
    <Form.Field className="vocabulary select remote" required={required}>
      <FieldValueProvider
        value={{ value: fieldValue, multiple, addValue, removeValue }}
      >
        {label}
        <label className="helptext">{helpText}</label>
        {!_isEmpty(fieldValue) && (
          <Grid.Row className="rel-mb-1">
            {(multiple && <VocabularyRemoteSelectValues />) || (
              <VocabularyRemoteSelectValue />
            )}
          </Grid.Row>
        )}
        <VocabularyRemoteSelectModal
          vocabulary={vocabulary}
          trigger={triggerButton}
          label={modalHeader}
          overriddenComponents={overriddenComponents}
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
