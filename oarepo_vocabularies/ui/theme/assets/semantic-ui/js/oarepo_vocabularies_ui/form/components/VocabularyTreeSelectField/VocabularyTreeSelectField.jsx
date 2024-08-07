import React, { useMemo, useState } from "react";
import { SelectField } from "react-invenio-forms";
import { useFormConfig } from "@js/oarepo_ui";
import { useFormikContext, getIn } from "formik";
import PropTypes from "prop-types";
import { processVocabularyItems } from "@js/oarepo_vocabularies";
import { TreeSelectFieldModal } from "./TreeSelectFieldModal";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

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
  let { all: allOptions } =
    vocabularies[optionsListName];

  if (!allOptions) {
    console.error(
      `Do not have options for ${optionsListName} inside:`,
      vocabularies
    );
  }

  const serializedOptions = useMemo(
    () => processVocabularyItems(allOptions, showLeafsOnly, filterFunction),
    [allOptions, showLeafsOnly, filterFunction]
  );

  const [openState, setOpenState] = useState(false);
  const [selectedState, setSelectedState] = useState([]);

  const handleOpen = (e) => {
    e.preventDefault();
    if (multiple && Array.isArray(value)) {
      const newSelectedState = value.reduce((acc, val) => {
        const foundOption = serializedOptions.find(
          (option) => option.value === val.id
        );
        if (foundOption) {
          acc.push(foundOption);
        }
        return acc;
      }, []);
      setSelectedState(newSelectedState);
    } else if (value) {
      const foundOption = serializedOptions.find(
        (option) => option.value === value.id
      );
      if (foundOption) {
        setSelectedState([foundOption]);
      } else {
        setSelectedState([]);
      }
    } else {
      setSelectedState([]);
    }

    setOpenState(true);
  };

  const handleSubmit = (newState) => {
    const prepSelect = [
      ...newState.map((item) => {
        return {
          id: item.value,
        };
      }),
    ];
    formik.setFieldValue(fieldPath, multiple ? prepSelect : prepSelect[0]);
    setOpenState(false);
    setSelectedState([]);
  };

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
        options={serializedOptions}
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
          allOptions={serializedOptions}
          root={root}
          value={value}
          handleSubmit={handleSubmit}
          selectedState={Array.isArray(selectedState) ? selectedState : []}
          setSelectedState={setSelectedState}
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
  placeholder: PropTypes.string,
  root: PropTypes.string,
  showLeafsOnly: PropTypes.bool,
  filterFunction: PropTypes.func,
};

VocabularyTreeSelectField.defaultProps = {
  noResultsMessage: i18next.t("No results found."),
  optimized: false,
  showLeafsOnly: false,
  filterFunction: undefined,
};
