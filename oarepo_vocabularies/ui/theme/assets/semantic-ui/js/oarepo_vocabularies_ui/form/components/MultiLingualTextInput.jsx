import React, { useEffect } from "react";
import PropTypes from "prop-types";
import {
  TextField,
  GroupField,
  ArrayField,
  FieldLabel,
  SelectField,
} from "react-invenio-forms";
import { Button, Form, Icon } from "semantic-ui-react";
import { useFormikContext, getIn } from "formik";
import _toPairs from "lodash/toPairs";
import _filter from "lodash/filter";
import { useFormConfig } from "@js/oarepo_ui/forms";
import { SelectInputField } from "./SelectInputField";

const translateObjectToArray = (obj) => {
  return _toPairs(obj).map(([language, title]) => ({ language, name: title }));
};

export const transformArrayToObject = (arr) => {
  const result = {};

  arr.forEach((obj) => {
    const { language, name } = obj;
    result[language] = name;
  });

  return result;
};

export const MultiLingualTextInput = ({
  fieldPath,
  label,
  labelIcon,
  required,
  emptyNewInput,
  newItemInitialValue,
  options,
}) => {
  // const {
  //   formConfig: { locales },
  // } = useFormConfig();
  const placeholderFieldPath = `_${fieldPath}`;
  const { setFieldValue, values } = useFormikContext();
  const currentlySelectedLanguages = getIn(values, placeholderFieldPath, []);
  //   ? Object.keys(getIn(values, fieldPath, {}))
  //   : [];
  // console.log(currentlySelectedLanguages);
  // const filteredOptions = _filter(
  //   options.languages,
  //   (obj) => !currentlySelectedLanguages.includes(obj.value)
  // );
  // console.log(filteredOptions);

  useEffect(() => {
    if (!getIn(values, placeholderFieldPath)) {
      setFieldValue(
        placeholderFieldPath,
        getIn(values, fieldPath)
          ? translateObjectToArray(getIn(values, fieldPath, ""))
          : translateObjectToArray(newItemInitialValue)
      );
      return;
    }
    setFieldValue(
      fieldPath,
      transformArrayToObject(getIn(values, placeholderFieldPath))
    );
  }, [values[placeholderFieldPath]]);

  return (
    <ArrayField
      addButtonLabel="Add another language"
      defaultNewValue={emptyNewInput}
      fieldPath={placeholderFieldPath}
      label={<FieldLabel htmlFor={fieldPath} icon="" label={label} />}
      required={required}
    >
      {({ arrayHelpers, indexPath }) => {
        const fieldPathPrefix = `${placeholderFieldPath}.${indexPath}`;

        return (
          <GroupField optimized>
            <SelectInputField
              clearable
              fieldPath={`${fieldPathPrefix}.language`}
              label="Language"
              optimized
              options={options.languages}
              required
              width={2}
              currentlySelectedLanguages={currentlySelectedLanguages}
            />

            <TextField
              fieldPath={`${fieldPathPrefix}.name`}
              label="Name"
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
  emptyNewInput: PropTypes.shape({
    language: PropTypes.string,
    name: PropTypes.string,
  }),
  newItemInitialValue: PropTypes.object,
};

MultiLingualTextInput.defaultProps = {
  label: "Title",
  required: undefined,
  emptyNewInput: {
    language: "",
    name: "",
  },
  newItemInitialValue: { cs: "" },
};
