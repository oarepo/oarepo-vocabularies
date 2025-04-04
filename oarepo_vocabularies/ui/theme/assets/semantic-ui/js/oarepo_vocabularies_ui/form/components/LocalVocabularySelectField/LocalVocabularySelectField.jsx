import React, { useMemo } from "react";
import { SelectField } from "react-invenio-forms";
import { useFormConfig, search, useFieldData } from "@js/oarepo_ui/forms";
import { useFormikContext, getIn } from "formik";
import PropTypes from "prop-types";
import { Dropdown, Divider } from "semantic-ui-react";
import { serializeVocabularyItems } from "@js/oarepo_vocabularies";

export const processVocabularyItems = (
  options,
  showLeafsOnly,
  filterFunction
) => {
  let serializedOptions = serializeVocabularyItems(options);
  if (showLeafsOnly) {
    serializedOptions = serializedOptions.filter(
      (o) => o.element_type === "leaf"
    );
  }
  if (filterFunction) {
    serializedOptions = filterFunction(serializedOptions);
  }
  return serializedOptions;
};

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
  optionsListName,
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

  const {
    formConfig: { vocabularies },
  } = useFormConfig();

  if (!vocabularies) {
    console.error("Do not have vocabularies in formConfig");
  }

  if (!vocabularies[optionsListName]) {
    console.error(
      "Vocabulary with name ",
      optionsListName,
      " not found in formConfig"
    );
  }

  const { all: allOptions, featured: featuredOptions } =
    vocabularies[optionsListName];

  if (!allOptions) {
    console.error(
      `Do not have options for ${optionsListName} inside:`,
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
  const hasMultipleItems = multiple || fieldData.detail === "array";

  const handleChange = ({ data, formikProps }) => {
    if (hasMultipleItems) {
      let vocabularyItems = allOptions.filter((o) =>
        data.value.includes(o.value)
      );
      vocabularyItems = vocabularyItems.map((vocabularyItem) => {
        return { ...vocabularyItem, id: vocabularyItem.value };
      });
      formikProps.form.setFieldValue(fieldPath, [...vocabularyItems]);
    } else {
      let vocabularyItem = allOptions.find((o) => o.value === data.value);
      vocabularyItem = data.value
        ? { ...vocabularyItem, id: vocabularyItem?.value }
        : {};
      formikProps.form.setFieldValue(fieldPath, vocabularyItem);
    }
  };

  const { values, setFieldTouched } = useFormikContext();
  const value = getIn(values, fieldPath, hasMultipleItems ? [] : {});
  return (
    <React.Fragment>
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
  optionsListName: PropTypes.string.isRequired,
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
