import React, { useEffect, useMemo } from "react";
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
import {
  array2object,
  object2array,
  eliminateUsedLanguages,
  useVocabularyOptions,
} from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const VocabularyMultilingualInput = ({
  fieldPath,
  label,
  labelIcon,
  required,
  emptyNewInput,
  newItemInitialValue,
  textFieldLabel,
}) => {
  const { options: languages } = useVocabularyOptions("languages");

  const placeholderFieldPath = useMemo(() => {
    return fieldPath
      .split(".")
      .map((part, index, array) =>
        index === array.length - 1 ? `_${part}` : part
      )
      .join(".");
  }, [fieldPath]);

  const { setFieldValue, values } = useFormikContext();
  useEffect(() => {
    if (!getIn(values, placeholderFieldPath)) {
      setFieldValue(
        placeholderFieldPath,
        getIn(values, fieldPath)
          ? object2array(getIn(values, fieldPath, ""), "language", "name")
          : object2array(newItemInitialValue, "language", "name")
      );
      return;
    }
    setFieldValue(
      fieldPath,
      array2object(getIn(values, placeholderFieldPath), "language", "name")
    );
  }, [values[placeholderFieldPath]]);

  return (
    <ArrayField
      addButtonLabel={i18next.t("Add another language")}
      defaultNewValue={emptyNewInput}
      fieldPath={placeholderFieldPath}
      label={
        <FieldLabel htmlFor={fieldPath} icon={labelIcon ?? ""} label={label} />
      }
      required={required}
    >
      {({ indexPath, array, arrayHelpers }) => {
        const fieldPathPrefix = `${placeholderFieldPath}.${indexPath}`;

        const availableOptions = eliminateUsedLanguages(
          indexPath,
          languages,
          array
        );

        return (
          <GroupField optimized>
            <Form.Field width={3}>
              <SelectField
                key={availableOptions.length}
                clearable
                fieldPath={`${fieldPathPrefix}.language`}
                label={i18next.t("Language")}
                optimized
                options={availableOptions}
                required={required}
                selectOnBlur={false}
              />
            </Form.Field>
            <TextField
              fieldPath={`${fieldPathPrefix}.name`}
              label={textFieldLabel}
              required={required}
              width={13}
            />
            {indexPath > 0 && (
              <Form.Field style={{ marginTop: "1.75rem" }}>
                <Button
                  aria-label={i18next.t("Remove field")}
                  className="close-btn"
                  icon
                  onClick={() => arrayHelpers.remove(indexPath)}
                >
                  <Icon name="close" />
                </Button>
              </Form.Field>
            )}
          </GroupField>
        );
      }}
    </ArrayField>
  );
};

VocabularyMultilingualInput.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  newItemInitialValue: PropTypes.object,
  textFieldLabel: PropTypes.string,
};

VocabularyMultilingualInput.defaultProps = {
  label: i18next.t("Title"),
  required: undefined,
  emptyNewInput: {
    language: "",
    name: "",
  },
  newItemInitialValue: { cs: "" },
  textFieldLabel: i18next.t("Name"),
};
