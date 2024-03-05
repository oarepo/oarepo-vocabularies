import React, { useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import { TextField, ArrayField, FieldLabel } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";
import {
  array2object,
  object2array,
  LanguageSelectField,
  ArrayFieldItem,
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
          <ArrayFieldItem
            indexPath={indexPath}
            array={array}
            arrayHelpers={arrayHelpers}
            displayRemoveButton={indexPath !== 0}
          >
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
          </ArrayFieldItem>
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
  emptyNewInput: PropTypes.object,
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
