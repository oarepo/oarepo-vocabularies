import React, { useState } from "react";
import { SelectField } from "react-invenio-forms";
import { useFormConfig } from "@js/oarepo_ui";
import { getIn, useFormikContext } from "formik";
import PropTypes from "prop-types";
import { TreeSelectFieldModal } from "./TreeSelectFieldModal";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { vocabularyItemsToColumnOptions } from "./util";

export const VocabularyTreeSelectField = ({
  fieldPath,
  multiple,
  optionsListName,
  helpText,
  placeholder,
  root,
  optimized,
  showLeafsOnly,
  filterFunction,
  ...uiProps
}) => {
  const { formConfig } = useFormConfig();
  const { vocabularies } = formConfig;
  const formik = useFormikContext();
  const { values, setFieldTouched } = useFormikContext();
  const value = getIn(values, fieldPath, multiple ? [] : {});
  const [openState, setOpenState] = useState(false);

  const { all: allOptions } = vocabularies[optionsListName];
  if (!allOptions) {
    console.error(
      `Do not have options for ${optionsListName} inside:`,
      vocabularies
    );
  }

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

  function getInitialSelections() {
    if (multiple && Array.isArray(value)) {
      return value
        .map((v) => serializedOptions.find((option) => option.value === v.id))
        .filter((v) => v);
    } else if (value) {
      return (
        serializedOptions.find((option) => option.value === value.id) || []
      );
    } else {
      return [];
    }
  }

  const [selectedState, setSelectedState] = useState(getInitialSelections);

  const handleOpen = React.useCallback((e = null) => {
    e?.preventDefault();
    setOpenState(true);
  }, []);

  const handleClose = React.useCallback((e = null) => {
    setOpenState(false);
  }, []);

  const handleSubmit = React.useCallback(
    (newState) => {
      const prepSelect = [
        ...newState.map((item) => {
          return {
            id: item.value,
          };
        }),
      ];
      formik.setFieldValue(fieldPath, multiple ? prepSelect : prepSelect[0]);
      handleClose();
    },
    [fieldPath, multiple]
  );

  return (
    <React.Fragment>
      <SelectField
        optimized={optimized}
        onBlur={() => setFieldTouched(fieldPath)}
        closeOnBlur
        closeOnChange
        open={false}
        openOnFocus={false}
        fieldPath={fieldPath}
        multiple={multiple}
        options={serializedOptions.map(({value, text}) => ({key: value, value, text: text}))}
        onOpen={(e) => handleOpen(e)}
        value={multiple ? value.map((o) => o?.id) : value?.id}
        {...uiProps}
      />
      <label className="helptext">{helpText}</label>

      {openState && (
        <TreeSelectFieldModal
          fieldPath={fieldPath}
          multiple={multiple}
          openState={openState}
          setOpenState={setOpenState}
          placeholder={placeholder}
          options={serializedOptions}
          onOpen={handleOpen}
          onClose={handleClose}
          value={value}
          root={root}
          showLeafsOnly={showLeafsOnly}
          filterFunction={filterFunction}
          handleSubmit={handleSubmit}
          selectedState={selectedState}
          setSelectedState={setSelectedState}
          vocabularyType={optionsListName}
        />
      )}
    </React.Fragment>
  );
};

VocabularyTreeSelectField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  multiple: PropTypes.bool,
  optionsListName: PropTypes.string.isRequired,
  helpText: PropTypes.string,
  noResultsMessage: PropTypes.string,
  optimized: PropTypes.bool,
  root: PropTypes.string,
  showLeafsOnly: PropTypes.bool,
  placeholder: PropTypes.string,
  filterFunction: PropTypes.func,
};

VocabularyTreeSelectField.defaultProps = {
  noResultsMessage: i18next.t("No results found."),
  optimized: false,
  showLeafsOnly: false,
  filterFunction: undefined,
};
