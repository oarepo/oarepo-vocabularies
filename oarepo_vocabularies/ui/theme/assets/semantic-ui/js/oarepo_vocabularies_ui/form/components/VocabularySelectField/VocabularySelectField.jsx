import React, { forwardRef } from "react";
import { useFieldData } from "@js/oarepo_ui/forms";
import { processVocabularyItems } from "../../util";
import PropTypes from "prop-types";
import { RemoteSelectField } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";
import _isEmpty from "lodash/isEmpty";

// for adding free text items
const serializeAddedValue = (value) => {
  return { text: value, value, key: value, name: value, id: value };
};

export const VocabularySelectField = forwardRef(
  (
    {
      vocabularyName,
      fieldPath,
      externalAuthority = false,
      multiple = false,
      filterFunction = (opt) => opt,
      icon,
      label,
      required,
      helpText,
      placeholder,
      fieldRepresentation,
      suggestionAPIHeaders = {
        Accept: "application/vnd.inveniordm.v1+json",
      },
      clearable = true,
      showLeafsOnly = false,
      ...restProps
    },
    ref
  ) => {
    const suggestionsConfig = {
      suggestionAPIUrl: `/api/vocabularies/${vocabularyName}`,
    };

    const { values } = useFormikContext();
    const { getFieldData } = useFieldData();

    const fieldData = {
      ...getFieldData({
        fieldPath,
        icon,
        fieldRepresentation,
      }),
      ...(label && { label }),
      ...(required && { required }),
      ...(helpText && { helpText }),
      ...(placeholder && { placeholder }),
    };

    const hasMultipleItems =
      multiple !== undefined ? multiple : fieldData.detail === "array";

    const initialSuggestions = hasMultipleItems
      ? getIn(values, fieldPath, [])
      : _isEmpty(getIn(values, fieldPath, {}))
      ? []
      : [getIn(values, fieldPath)];

    const value = hasMultipleItems
      ? getIn(values, fieldPath, [])
      : getIn(values, fieldPath, {});

    function _serializeSuggestions(suggestions) {
      return processVocabularyItems(suggestions, showLeafsOnly, filterFunction);
    }

    return (
      <>
        <RemoteSelectField
          fieldPath={fieldPath}
          {...suggestionsConfig}
          selectOnBlur={false}
          serializeSuggestions={_serializeSuggestions}
          multiple={hasMultipleItems}
          deburr
          serializeAddedValue={serializeAddedValue}
          initialSuggestions={initialSuggestions}
          suggestionAPIHeaders={suggestionAPIHeaders}
          clearable={clearable}
          onValueChange={({ e, data, formikProps }, selectedSuggestions) => {
            if (hasMultipleItems) {
              const vocabularyItems = selectedSuggestions
                .filter((o) => data.value.includes(o.id))
                .map((vocabularyItem) => ({
                  id: vocabularyItem.id,
                  text: vocabularyItem.text,
                }));

              formikProps.form.setFieldValue(fieldPath, [...vocabularyItems]);
            } else {
              const vocabularyItem = selectedSuggestions.find(
                (o) => o.id === data.value
              );
              if (vocabularyItem) {
                formikProps.form.setFieldValue(fieldPath, {
                  id: vocabularyItem.id,
                  text: vocabularyItem.text,
                });
              } else {
                formikProps.form.setFieldValue(fieldPath, "");
              }
            }
          }}
          value={
            hasMultipleItems ? value.map((item) => item.id) : value.id ?? ""
          }
          ref={ref}
          {...fieldData}
          {...restProps}
        />
        {fieldData?.helpText && (
          <label className="helptext">{fieldData.helpText}</label>
        )}
      </>
    );
  }
);

VocabularySelectField.displayName = "VocabularySelectField";

/* eslint-disable react/require-default-props */
VocabularySelectField.propTypes = {
  vocabularyName: PropTypes.string.isRequired,
  fieldPath: PropTypes.string.isRequired,
  externalAuthority: PropTypes.bool,
  multiple: PropTypes.bool,
  filterFunction: PropTypes.func,
  icon: PropTypes.string,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  required: PropTypes.bool,
  helpText: PropTypes.string,
  placeholder: PropTypes.string,
  fieldRepresentation: PropTypes.string,
  clearable: PropTypes.bool,
  suggestionAPIHeaders: PropTypes.object,
  showLeafsOnly: PropTypes.bool,
};
/* eslint-enable react/require-default-props */
