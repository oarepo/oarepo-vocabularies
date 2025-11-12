import React from "react";
import PropTypes from "prop-types";
import { TextField, ArrayField, FieldLabel } from "react-invenio-forms";
import { LanguageSelectField, ArrayFieldItem } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const VocabularyMultilingualInputField = ({
  fieldPath,
  label = i18next.t("Title"),
  labelIcon,
  required,
  emptyNewInput = {
    language: "",
    name: "",
  },
  textFieldLabel = i18next.t("Name"),
  displayFirstInputRemoveButton = true,
  helpText,
}) => {
  return (
    <ArrayField
      addButtonLabel={i18next.t("Add another language")}
      defaultNewValue={emptyNewInput}
      showEmptyValue
      fieldPath={fieldPath}
      label={
        <FieldLabel htmlFor={fieldPath} icon={labelIcon ?? ""} label={label} />
      }
      required={required}
      addButtonClassName="array-field-add-button"
      helpText={helpText}
    >
      {({ indexPath, arrayHelpers, array }) => {
        const fieldPathPrefix = `${fieldPath}.${indexPath}`;
        return (
          <ArrayFieldItem
            indexPath={indexPath}
            arrayHelpers={arrayHelpers}
            displayFirstInputRemoveButton={displayFirstInputRemoveButton}
            fieldPathPrefix={fieldPathPrefix}
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
              fieldPath={`${fieldPathPrefix}.value`}
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

/* eslint-disable react/require-default-props */
VocabularyMultilingualInputField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  textFieldLabel: PropTypes.string,
  emptyNewInput: PropTypes.object,
  displayFirstInputRemoveButton: PropTypes.bool,
  helpText: PropTypes.string,
};
/* eslint-enable react/require-default-props */
