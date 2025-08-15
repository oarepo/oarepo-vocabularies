import React, { useMemo, forwardRef } from "react";
import { SelectField } from "react-invenio-forms";
import { useFormConfig, search, useFieldData } from "@js/oarepo_ui/forms";
import { useFormikContext, getIn } from "formik";
import PropTypes from "prop-types";
import { Dropdown, Divider } from "semantic-ui-react";
import { processVocabularyItems } from "../../util";

const InnerDropdown = ({
  options = [],
  featured = [],
  usedOptions = [],
  value,
  ...rest
}) => {
  const _filterUsed = (opts) =>
    opts.filter((o) => !usedOptions.includes(o.value) || o.value === value);

  const allOptions = _filterUsed([
    ...(featured.length
      ? [
          ...featured.sort((a, b) => a.name.localeCompare(b.name)),
          {
            content: <Divider fitted />,
            disabled: true,
            key: "featured-divider",
          },
        ]
      : []),
    ...options.filter((o) => !featured.map((f) => f.value).includes(o.value)),
  ]);

  return (
    <Dropdown search={search} options={allOptions} value={value} {...rest} />
  );
};

/* eslint-disable react/require-default-props */
InnerDropdown.propTypes = {
  options: PropTypes.array.isRequired,
  featured: PropTypes.array,
  usedOptions: PropTypes.array,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string),
  ]),
};
/* eslint-enable react/require-default-props */

export const LocalVocabularySelectField = forwardRef(
  (
    {
      fieldPath,
      fieldRepresentation,
      multiple,
      vocabularyName,
      usedOptions = [],
      helpText,
      placeholder,
      showLeafsOnly = false,
      optimized = true,
      filterFunction = undefined,
      icon = "tag",
      clearable = true,
      label,
      required,
      ...uiProps
    },
    ref
  ) => {
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

    const { helpText: help, ...restFieldData } = fieldData;
    const hasMultipleItems =
      multiple !== undefined ? multiple : fieldData.detail === "array";

    const { values, setFieldTouched } = useFormikContext();
    const value = getIn(values, fieldPath, hasMultipleItems ? [] : {});

    const {
      formConfig: { vocabularies },
    } = useFormConfig();

    if (!vocabularies) {
      console.error("Do not have vocabularies in formConfig");
    }

    const { all: allOptions = [], featured: featuredOptions = [] } =
      vocabularies[vocabularyName] || {};

    if (allOptions.length === 0) {
      console.error(
        `Do not have options for ${vocabularyName} inside:`,
        vocabularies
      );
    }

    const serializedOptions = useMemo(
      () => processVocabularyItems(allOptions, showLeafsOnly, filterFunction),
      [allOptions, showLeafsOnly, filterFunction]
    );

    const serializedFeaturedOptions = useMemo(
      () =>
        processVocabularyItems(featuredOptions, showLeafsOnly, filterFunction),
      [featuredOptions, showLeafsOnly, filterFunction]
    );

    const handleChange = ({ data, formikProps }) => {
      if (hasMultipleItems) {
        const vocabularyItems = serializedOptions
          .filter((o) => data.value.includes(o.id))
          .map((vocabularyItem) => ({ id: vocabularyItem.id }));

        formikProps.form.setFieldValue(fieldPath, [...vocabularyItems]);
      } else {
        const foundVocabularyItem = serializedOptions.find(
          (o) => o.id === data.value
        );
        const vocabularyItem = data.value
          ? { id: foundVocabularyItem?.id }
          : {};
        formikProps.form.setFieldValue(fieldPath, vocabularyItem);
      }
    };

    if (!vocabularies[vocabularyName]) {
      throw new Error(
        `Vocabulary with name "${vocabularyName}" not found in formConfig`
      );
    }
    return (
      <>
        <SelectField
          selectOnBlur={false}
          optimized={optimized}
          onBlur={() => setFieldTouched(fieldPath)}
          deburr
          search={search}
          control={InnerDropdown}
          fieldPath={fieldPath}
          multiple={hasMultipleItems}
          featured={serializedFeaturedOptions}
          options={serializedOptions}
          usedOptions={usedOptions}
          onChange={handleChange}
          value={hasMultipleItems ? value.map((o) => o?.id) : value?.id}
          ref={ref}
          clearable={clearable}
          {...restFieldData}
          {...uiProps}
        />
        <label className="helptext">{help}</label>
      </>
    );
  }
);

LocalVocabularySelectField.displayName = "LocalVocabularySelectField";
/* eslint-disable react/require-default-props */
LocalVocabularySelectField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  fieldRepresentation: PropTypes.string,
  multiple: PropTypes.bool,
  vocabularyName: PropTypes.string.isRequired,
  helpText: PropTypes.string,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  placeholder: PropTypes.string,
  required: PropTypes.bool,
  usedOptions: PropTypes.array,
  showLeafsOnly: PropTypes.bool,
  optimized: PropTypes.bool,
  filterFunction: PropTypes.func,
  icon: PropTypes.string,
  clearable: PropTypes.bool,
};
/* eslint-enable react/require-default-props */
