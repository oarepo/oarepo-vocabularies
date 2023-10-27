import React, { useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import {
  TextField,
  GroupField,
  ArrayField,
  FieldLabel,
} from "react-invenio-forms";
import { Button, Form, Icon } from "semantic-ui-react";
import { useFormikContext, getIn } from "formik";
import {
  array2object,
  object2array,
  LanguageSelectField,
} from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const VocabularyMultilingualInputField = ({
  fieldPath,
  label,
  labelIcon,
  required,
  emptyNewInput,
  newItemInitialValue,
  textFieldLabel,
}) => {
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
          ? object2array(getIn(values, fieldPath, ""), "lang", "name")
          : object2array(newItemInitialValue, "lang", "name")
      );
      return;
    }
    setFieldValue(
      fieldPath,
      array2object(getIn(values, placeholderFieldPath), "lang", "name")
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
        return (
          <GroupField optimized>
            <LanguageSelectField
              fieldPath={`${fieldPathPrefix}.lang`}
              placeholder=""
              required
              optimized
              clearable
              width={3}
              usedLanguages={array.map((v) => v.lang)}
            />
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

VocabularyMultilingualInputField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  newItemInitialValue: PropTypes.object,
  textFieldLabel: PropTypes.string,
};

VocabularyMultilingualInputField.defaultProps = {
  label: i18next.t("Title"),
  required: undefined,
  emptyNewInput: {
    language: "",
    name: "",
  },
  newItemInitialValue: { cs: "" },
  textFieldLabel: i18next.t("Name"),
};
