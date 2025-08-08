import React, { useMemo } from "react";
import { SelectField } from "react-invenio-forms";
import { useFormConfig, search, useFieldData } from "@js/oarepo_ui/forms";
import { useFormikContext, getIn } from "formik";
import PropTypes from "prop-types";
import { Dropdown, Divider } from "semantic-ui-react";
import { processVocabularyItems } from "@js/oarepo_vocabularies";

const InnerDropdown = ({
  options,
  featured,
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
    ...options.filter((o) => !featured.map((o) => o.value).includes(o.value)),
  ]);

  return (
    <Dropdown search={search} options={allOptions} value={value} {...rest} />
  );
};

InnerDropdown.propTypes = {
  options: PropTypes.array.isRequired,
  featured: PropTypes.array,
  usedOptions: PropTypes.array,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string),
  ]),
};
export const LocalVocabularySelectField = ({
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
  ref,
  ...uiProps
}) => {
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

  // Remove helpText from fieldData to avoid passing it to the SelectField
  const { helpText: help, ...restFieldData } = fieldData;
  const hasMultipleItems = multiple || fieldData.detail === "array";

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

  let serializedOptions = useMemo(
    () => processVocabularyItems(allOptions, showLeafsOnly, filterFunction),
    [allOptions, showLeafsOnly, filterFunction]
  );

  let serializedFeaturedOptions = useMemo(
    () =>
      processVocabularyItems(featuredOptions, showLeafsOnly, filterFunction),
    [featuredOptions, showLeafsOnly, filterFunction]
  );

  const handleChange = ({ data, formikProps }) => {
    if (hasMultipleItems) {
      let vocabularyItems = serializedOptions.filter((o) =>
        data.value.includes(o.id)
      );
      vocabularyItems = vocabularyItems.map((vocabularyItem) => {
        return { id: vocabularyItem.id };
      });
      formikProps.form.setFieldValue(fieldPath, [...vocabularyItems]);
    } else {
      let vocabularyItem = serializedOptions.find((o) => o.id === data.value);
      vocabularyItem = data.value ? { id: vocabularyItem?.id } : {};
      formikProps.form.setFieldValue(fieldPath, vocabularyItem);
    }
  };

  const customSearch = (options, searchQuery) =>
    search(options, searchQuery, "text");

  if (!vocabularies[vocabularyName]) {
    console.error(
      "Vocabulary with name ",
      vocabularyName,
      " not found in formConfig"
    );
    return (
      <div className="rel-mt-2 rel-mb-2">
        <strong>
          Vocabulary not found: `Vocabulary with name ${vocabularyName} not
          found in formConfig`
        </strong>
      </div>
    );
  }

  return (
    <React.Fragment>
      <SelectField
        selectOnBlur={false}
        optimized={optimized}
        onBlur={() => setFieldTouched(fieldPath)}
        deburr
        search={customSearch}
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
    </React.Fragment>
  );
};

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
