import React from "react";
import PropTypes from "prop-types";
import { ArrayField, TextField } from "react-invenio-forms";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import {
  ArrayFieldItem,
  useFieldData,
  useValidateOnBlur,
} from "@js/oarepo_ui/forms";
import { useFormikContext } from "formik";
import { mergeFieldData } from "@js/oarepo_ui/forms/util";

/**
 * GenericIdentifiersField - A component for managing identifiers/crosswalks
 * with free-text scheme input instead of a dropdown.
 *
 * This allows users to enter any arbitrary scheme value, unlike the standard
 * IdentifiersField which requires a predefined list of schemes.
 */
export const GenericIdentifiersField = ({
  fieldPath,
  labelIcon = "pencil",
  className = "",
  defaultNewValue = { scheme: "", identifier: "" },
  validateOnBlur = false,
  label,
  required,
  helpText,
  addButtonLabel,
  schemePlaceholder = i18next.t("IRI of the scheme"),
  identifierPlaceholder = i18next.t("Identifier value (mostly as an IRI)"),
  ...uiProps
}) => {
  const { setFieldTouched } = useFormikContext();
  const { getFieldData } = useFieldData();
  const handleValidateAndBlur = useValidateOnBlur();

  const fieldDataProps = mergeFieldData(
    getFieldData({
      fieldPath,
      icon: labelIcon,
      fieldRepresentation: "text",
    }),
    { label, required, helpText }
  );

  const schemeFieldProps = {
    ...getFieldData({
      fieldPath: `${fieldPath}.0.scheme`,
      fieldRepresentation: "compact",
    }),
    label: i18next.t("Scheme"),
  };

  const identifierFieldProps = {
    ...getFieldData({
      fieldPath: `${fieldPath}.0.identifier`,
      fieldRepresentation: "compact",
    }),
    label: i18next.t("Identifier"),
  };

  return (
    <ArrayField
      addButtonLabel={addButtonLabel || i18next.t("Add identifier")}
      fieldPath={fieldPath}
      className={className}
      defaultNewValue={defaultNewValue}
      {...fieldDataProps}
      addButtonClassName="array-field-add-button"
    >
      {({ arrayHelpers, indexPath }) => {
        const fieldPathPrefix = `${fieldPath}.${indexPath}`;
        const schemeFieldPath = `${fieldPathPrefix}.scheme`;
        const identifierFieldPath = `${fieldPathPrefix}.identifier`;
        return (
          <ArrayFieldItem
            indexPath={indexPath}
            arrayHelpers={arrayHelpers}
            fieldPathPrefix={fieldPathPrefix}
          >
            <TextField
              width={5}
              fieldPath={schemeFieldPath}
              placeholder={schemePlaceholder}
              onBlur={
                validateOnBlur
                  ? () => handleValidateAndBlur(schemeFieldPath)
                  : () => setFieldTouched(schemeFieldPath)
              }
              {...schemeFieldProps}
              {...uiProps}
            />
            <TextField
              width={11}
              fieldPath={identifierFieldPath}
              placeholder={identifierPlaceholder}
              {...identifierFieldProps}
              onBlur={
                validateOnBlur
                  ? () => handleValidateAndBlur(identifierFieldPath)
                  : () => setFieldTouched(identifierFieldPath)
              }
            />
          </ArrayFieldItem>
        );
      }}
    </ArrayField>
  );
};

GenericIdentifiersField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  /* eslint-disable react/require-default-props */
  labelIcon: PropTypes.string,
  className: PropTypes.string,
  defaultNewValue: PropTypes.object,
  validateOnBlur: PropTypes.bool,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  required: PropTypes.bool,
  helpText: PropTypes.string,
  addButtonLabel: PropTypes.string,
  schemePlaceholder: PropTypes.string,
  identifierPlaceholder: PropTypes.string,
  /* eslint-enable react/require-default-props */
};
