import React, { useState, useMemo } from "react";
import { useFormConfig } from "@js/oarepo_ui";
import { getIn, useFormikContext } from "formik";
import PropTypes from "prop-types";
import { TreeSelectFieldModal } from "./TreeSelectFieldModal";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { vocabularyItemsToColumnOptions } from "./util";
import { VocabularyPickerField } from "../VocabularyPickerField";
import { useModalTrigger } from "../../hooks";

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
  // it looks clunky, but unfortunately, when this field is empty, the getIn,
  // creates new object or array every time, and it causes constant rerendering

  const emptyArray = useMemo(() => [], []);
  const emptyObject = useMemo(() => ({}), []);
  const value = getIn(values, fieldPath, multiple ? emptyArray : emptyObject);

  const { all: allOptions } = vocabularies[vocabulary];
  if (!allOptions) {
    console.error(`Missing options for ${vocabulary} inside:`, vocabularies);
  }
  const handleSubmit = React.useCallback(
    (currentValue) => {
      const newValue = currentValue.map((item) => ({
        id: item.value,
        title: { [i18next.language]: item.name },
      }));
      setFieldValue(fieldPath, multiple ? newValue : newValue[0]);
    },
    [fieldPath, multiple, setFieldValue]
  );

  return (
    <MemoizedVocabularyTreeSelectPresentation
      fieldPath={fieldPath}
      label={label}
      helpText={helpText}
      multiple={multiple}
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
  showLeafsOnly,
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
  const [selected, setSelected] = useState(() => getCurrentSelections());

  const _trigger = useModalTrigger({
    value,
    trigger: triggerButton,
  });

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
    }
    return [];
  }

  const handleSelect = React.useCallback((newValue) => {
    if (typeof newValue === "function") {
      setSelected((prevValue) => newValue(prevValue));
    } else {
      setSelected(newValue);
    }
  }, []);

  const handleChange = React.useCallback((newValue) => {
    const newSelected = getCurrentSelections(newValue);
    setSelected(newSelected);
  }, []);

  const handleModalClose = React.useCallback(() => {
    setSelected(getCurrentSelections());
  }, [value, serializedOptions]);

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
  value: PropTypes.array,
  allOptions: PropTypes.array,
  onSubmit: PropTypes.func,
};

VocabularyTreeSelectPresentation.defaultProps = {
  showLeafsOnly: false,
  filterFunction: undefined,
  multiple: false,
  required: false,
};

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
VocabularyTreeSelectField.propTypes = {
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

VocabularyTreeSelectField.defaultProps = {
  showLeafsOnly: false,
  filterFunction: undefined,
  multiple: false,
  required: false,
};
