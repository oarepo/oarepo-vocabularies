import React, { useState } from "react";
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
  triggerButton,
  showLeafsOnly,
  filterFunction,
  ...uiProps
}) => {
  const { formConfig } = useFormConfig();
  const { vocabularies } = formConfig;
  const formik = useFormikContext();
  const { values } = useFormikContext();
  const value = getIn(values, fieldPath, multiple ? [] : {});

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
      <TreeSelectFieldModal
        fieldPath={fieldPath}
        multiple={multiple}
        placeholder={placeholder}
        options={serializedOptions}
        value={value}
        root={root}
        showLeafsOnly={showLeafsOnly}
        filterFunction={filterFunction}
        onSubmit={handleSubmit}
        selectedState={selectedState}
        setSelectedState={setSelectedState}
        trigger={triggerButton}
        vocabularyType={optionsListName}
        {...uiProps}
      />
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
  triggerButton: PropTypes.node,
};

VocabularyTreeSelectField.defaultProps = {
  noResultsMessage: i18next.t("No results found."),
  optimized: false,
  showLeafsOnly: false,
  filterFunction: undefined,
};
