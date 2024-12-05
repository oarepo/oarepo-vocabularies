import React, { useState } from "react";
import { useFormConfig } from "@js/oarepo_ui";
import { getIn, useFormikContext } from "formik";
import PropTypes from "prop-types";
import { TreeSelectFieldModal } from "./TreeSelectFieldModal";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { vocabularyItemsToColumnOptions } from "./util";
import { VocabularyPickerField } from "../VocabularyPickerField";

export const VocabularyTreeSelectField = ({
  vocabulary,
  fieldPath,
  label,
  helpText,
  multiple,
  required,
  triggerButton,
  placeholder,
  root,
  showLeafsOnly,
  filterFunction,
  ...restProps
}) => {
  const { formConfig } = useFormConfig();
  const { vocabularies } = formConfig;
  const { values, setFieldValue } = useFormikContext();
  const [selected, setSelected] = useState(getCurrentSelections);

  const value = getIn(values, fieldPath, multiple ? [] : {});

  const { all: allOptions } = vocabularies[vocabulary];
  if (!allOptions) {
    console.error(`Missing options for ${vocabulary} inside:`, vocabularies);
  }

  const serializedOptions = React.useMemo(
    () =>
      vocabularyItemsToColumnOptions(
        allOptions,
        root,
        showLeafsOnly,
        filterFunction
      ),
    [value, allOptions, root, showLeafsOnly, filterFunction]
  );

  function getCurrentSelections(newValue = null) {
    const _value = newValue || value;

    if (multiple && Array.isArray(_value)) {
      return _value
        .map((v) => serializedOptions.find((option) => option.value === v.id))
        .filter((v) => v);
    } else if (_value) {
      return (
        serializedOptions.find((option) => option.value === _value.id) || []
      );
    } else {
      return [];
    }
  }

  const handleSelect = React.useCallback((newValue) => {
    if (typeof newValue === "function") {
      setSelected((prevValue) => newValue(prevValue));
    } else {
      setSelected(newValue);
    }
  });

  const handleChange = (newValue) => {
    const newSelected = getCurrentSelections(newValue);
    setSelected(newSelected);
  };

  const handleModalClose = () => {
    setSelected(getCurrentSelections())
  }

  const handleSubmit = React.useCallback(
    (currentValue) => {
      const newValue = [
        ...currentValue.map((item) => {
          return {
            id: item.value,
            title: { [i18next.language]: item.name },
          };
        }),
      ];
      setFieldValue(fieldPath, multiple ? newValue : newValue[0]);
    },
    [fieldPath, multiple]
  );

  return (
    <VocabularyPickerField
      className="tree select"
      fieldPath={fieldPath}
      label={label}
      helpText={helpText}
      multiple={multiple}
      required={required}
      onChange={handleChange}
    >
      <TreeSelectFieldModal
        fieldPath={fieldPath}
        multiple={multiple}
        placeholder={placeholder}
        options={serializedOptions}
        value={value}
        onClose={handleModalClose}
        root={root}
        showLeafsOnly={showLeafsOnly}
        filterFunction={filterFunction}
        onSubmit={handleSubmit}
        onSelect={handleSelect}
        selected={selected}
        trigger={triggerButton}
        vocabularyType={vocabulary}
        {...restProps}
      />
    </VocabularyPickerField>
  );
};

VocabularyTreeSelectField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  multiple: PropTypes.bool,
  vocabulary: PropTypes.string.isRequired,
  helpText: PropTypes.string,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  required: PropTypes.bool,
  optimized: PropTypes.bool,
  root: PropTypes.string,
  showLeafsOnly: PropTypes.bool,
  placeholder: PropTypes.string,
  filterFunction: PropTypes.func,
  triggerButton: PropTypes.node,
};

VocabularyTreeSelectField.defaultProps = {
  optimized: false,
  showLeafsOnly: false,
  filterFunction: undefined,
  multiple: false,
  required: false,
};
