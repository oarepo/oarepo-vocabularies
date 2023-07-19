import React from "react";
import PropTypes from "prop-types";
import {
  TextField,
  GroupField,
  ArrayField,
  FieldLabel,
  SelectField,
} from "react-invenio-forms";
import { Button, Form, Icon } from "semantic-ui-react";

const emptyNewInput = {
  language: "",
  title: "",
};

export const MultiLingualTextInput = ({
  fieldPath,
  label,
  labelIcon,
  required,
  options,
  showEmptyValue,
}) => {
  console.log("dsadsaddsfds");
  return (
    <ArrayField
      addButtonLabel="Add another language"
      defaultNewValue={emptyNewInput}
      fieldPath={fieldPath}
      label={<FieldLabel htmlFor={fieldPath} icon="" label={label} />}
      required={required}
      showEmptyValue={showEmptyValue}
    >
      {({ arrayHelpers, indexPath }) => {
        const fieldPathPrefix = `${fieldPath}.${indexPath}`;

        return (
          <GroupField optimized>
            <SelectField
              clearable
              fieldPath={`${fieldPathPrefix}.language`}
              label="Language"
              optimized
              options={options.languages}
              required
              width={2}
            />

            <TextField
              fieldPath={`${fieldPathPrefix}.title`}
              label="Title"
              width={9}
              required
            />

            <Form.Field>
              {indexPath > 0 && (
                <Button
                  style={{ marginTop: "1.75rem" }}
                  aria-label="remove field"
                  className="close-btn"
                  icon
                  onClick={() => arrayHelpers.remove(indexPath)}
                >
                  <Icon name="close" />
                </Button>
              )}
            </Form.Field>
          </GroupField>
        );
      }}
    </ArrayField>
  );
};

MultiLingualTextInput.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  options: PropTypes.object.isRequired,
  showEmptyValue: PropTypes.bool,
};

MultiLingualTextInput.defaultProps = {
  label: "Title",
  labelIcon: "barcode",
  required: undefined,
  showEmptyValue: false,
};
