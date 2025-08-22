import React, { useState, useMemo } from "react";
import { getIn, useFormikContext } from "formik";
import PropTypes from "prop-types";
import { TreeSelectFieldModal } from "./TreeSelectFieldModal";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { vocabularyItemsToColumnOptions } from "./util";
import { VocabularyPickerField } from "../VocabularyPickerField";
import { useModalTrigger } from "../../hooks";
import { useFieldData, useFormConfig } from "@js/oarepo_ui/forms";

export const VocabularyTreeSelectField = ({
  vocabulary,
  fieldPath,
  label,
  helpText,
  icon = "tag",
  multiple,
  required,
  triggerButton,
  placeholder,
  root,
  showLeafsOnly = false,
  filterFunction,
  ...restProps
}) => {
  const { formConfig } = useFormConfig();
  const { vocabularies } = formConfig;
  const { values, setFieldValue } = useFormikContext();
  // it looks clunky, but unfortunately, when this field is empty, the getIn,
  // creates new object or array every time, and it causes constant rerendering

  const { getFieldData } = useFieldData();

  const fieldData = {
    ...getFieldData({
      fieldPath: fieldPath,
      icon: icon,
    }),
    ...(label && { label }),
    ...(required && { required }),
    ...(helpText && { helpText }),
  };
  const hasMultipleItems =
    multiple !== undefined ? multiple : fieldData.detail === "array";

  const emptyArray = useMemo(() => [], []);
  const emptyObject = useMemo(() => ({}), []);
  const value = getIn(
    values,
    fieldPath,
    hasMultipleItems ? emptyArray : emptyObject
  );

  const allOptions = vocabularies?.[vocabulary]?.all;

  const handleSubmit = React.useCallback(
    (currentValue) => {
      const newValue = currentValue.map((item) => ({
        id: item.value,
        title: { [i18next.language]: item.name },
      }));
      setFieldValue(fieldPath, hasMultipleItems ? newValue : newValue[0]);
    },
    [fieldPath, hasMultipleItems, setFieldValue]
  );

  if (!allOptions) {
    console.error(`Missing options for ${vocabulary} inside:`, vocabularies);
    return null;
  }

  return (
    <MemoizedVocabularyTreeSelectPresentation
      fieldPath={fieldPath}
      label={label}
      helpText={helpText}
      multiple={hasMultipleItems}
      required={required}
      triggerButton={triggerButton}
      placeholder={placeholder}
      root={root}
      showLeafsOnly={showLeafsOnly}
      filterFunction={filterFunction}
      value={value}
      allOptions={allOptions}
      onSubmit={handleSubmit}
      vocabulary={vocabulary}
      {...fieldData}
      {...restProps}
    />
  );
};
const VocabularyTreeSelectPresentation = ({
  fieldPath,
  label,
  helpText,
  multiple,
  required,
  triggerButton,
  placeholder,
  root,
  showLeafsOnly = false,
  filterFunction,
  value,
  allOptions,
  onSubmit,
  vocabulary,
  ...restProps
}) => {
  const serializedOptions = React.useMemo(
    () =>
      vocabularyItemsToColumnOptions(
        allOptions,
        root,
        showLeafsOnly,
        filterFunction
      ),
    [allOptions, root, showLeafsOnly, filterFunction]
  );

  const getCurrentSelections = React.useCallback(
    (newValue = null) => {
      const _value = newValue || value;

      if (multiple && Array.isArray(_value)) {
        return _value
          .map((v) => serializedOptions.find((option) => option.value === v.id))
          .filter((v) => v);
      } else if (_value) {
        return (
          serializedOptions.find((option) => option.value === _value.id) || []
        );
      }
      return [];
    },
    [value, multiple, serializedOptions]
  );

  const [selected, setSelected] = useState(() => getCurrentSelections());

  const _trigger = useModalTrigger({
    value,
    trigger: triggerButton,
  });

  const handleSelect = React.useCallback((newValue) => {
    if (typeof newValue === "function") {
      setSelected((prevValue) => newValue(prevValue));
    } else {
      setSelected(newValue);
    }
  }, []);

  const handleChange = React.useCallback(
    (newValue) => {
      const newSelected = getCurrentSelections(newValue);
      setSelected(newSelected);
    },
    [getCurrentSelections]
  );

  const handleModalClose = React.useCallback(() => {
    setSelected(getCurrentSelections());
  }, [getCurrentSelections]);

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
        onSubmit={onSubmit}
        onSelect={handleSelect}
        selected={selected}
        trigger={_trigger}
        vocabularyType={vocabulary}
        {...restProps}
      />
    </VocabularyPickerField>
  );
};

/* eslint-disable react/require-default-props */
VocabularyTreeSelectPresentation.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  multiple: PropTypes.bool,
  vocabulary: PropTypes.string.isRequired,
  helpText: PropTypes.string,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  required: PropTypes.bool,
  root: PropTypes.string,
  showLeafsOnly: PropTypes.bool,
  placeholder: PropTypes.string,
  filterFunction: PropTypes.func,
  triggerButton: PropTypes.node,
  value: PropTypes.oneOfType([PropTypes.object, PropTypes.array]).isRequired,
  allOptions: PropTypes.array,
  onSubmit: PropTypes.func,
};
/* eslint-enable react/require-default-props */

const MemoizedVocabularyTreeSelectPresentation = React.memo(
  VocabularyTreeSelectPresentation,
  (prevProps, nextProps) => {
    return (
      prevProps.value === nextProps.value &&
      prevProps.allOptions === nextProps.allOptions &&
      prevProps.root === nextProps.root &&
      prevProps.showLeafsOnly === nextProps.showLeafsOnly &&
      prevProps.filterFunction === nextProps.filterFunction
    );
  }
);

/* eslint-disable react/require-default-props */
VocabularyTreeSelectField.propTypes = {
  icon: PropTypes.string,
  fieldPath: PropTypes.string.isRequired,
  multiple: PropTypes.bool,
  vocabulary: PropTypes.string.isRequired,
  helpText: PropTypes.string,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  required: PropTypes.bool,
  root: PropTypes.string,
  showLeafsOnly: PropTypes.bool,
  placeholder: PropTypes.string,
  filterFunction: PropTypes.func,
  triggerButton: PropTypes.node,
};
/* eslint-enable react/require-default-props */
