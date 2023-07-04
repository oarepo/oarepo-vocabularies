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

const emptyRelatedWork = {
  language: "",
  title: "",
};

export const FieldWithLanguageOption = ({
  fieldPath,
  label,
  labelIcon,
  required,
  options,
  showEmptyValue,
}) => {
  return (
    <ArrayField
      addButtonLabel="Add another language"
      defaultNewValue={emptyRelatedWork}
      fieldPath={fieldPath}
      label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
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
              <Button
                aria-label="remove field"
                className="close-btn"
                icon
                onClick={() => arrayHelpers.remove(indexPath)}
              >
                <Icon name="close" />
              </Button>
            </Form.Field>
          </GroupField>
        );
      }}
    </ArrayField>
  );
};

FieldWithLanguageOption.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  options: PropTypes.object.isRequired,
  showEmptyValue: PropTypes.bool,
};

FieldWithLanguageOption.defaultProps = {
  label: "Title",
  labelIcon: "barcode",
  required: undefined,
  showEmptyValue: false,
};
