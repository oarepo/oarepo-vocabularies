import React, { useMemo, useState } from "react";
import { SelectField } from "react-invenio-forms";
import { useFormConfig } from "@js/oarepo_ui";
import { useFormikContext, getIn } from "formik";
import PropTypes from "prop-types";
import { processVocabularyItems } from "@js/oarepo_vocabularies";
import { TreeSelectFieldModal } from "./TreeSelectFieldModal";

export const VocabularyTreeSelectField = ({
  fieldPath,
  multiple,
  optionsListName,
  helpText,
  placeholder,
  root,
  optimized,
  ...uiProps
}) => {
  const { formConfig } = useFormConfig();
  const { vocabularies } = formConfig;
  const formik = useFormikContext();
  const { values, setFieldTouched } = useFormikContext();
  const value = getIn(values, fieldPath, multiple ? [] : {});
  let { all: allOptions, featured: featuredOptions } =
    vocabularies[optionsListName];

  if (!allOptions) {
    console.error(
      `Do not have options for ${optionsListName} inside:`,
      vocabularies
    );
  }

  const serializedOptions = useMemo(
    () => processVocabularyItems(allOptions),
    [allOptions]
  );

  const [openState, setOpenState] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedState, setSelectedState] = useState(() => {
    if (multiple && Array.isArray(value)) {
      return value.reduce((acc, val) => {
        const foundOption = serializedOptions.find(
          (option) => option.value === val.id
        );
        if (foundOption) {
          acc.push(foundOption);
        }
        return acc;
      }, []);
    } else {
      return [];
    }
  });

  const handleChange = ({ e, data }) => {
    if (multiple) {
      let vocabularyItems = allOptions.filter((o) =>
        data.value.includes(o.value)
      );
      vocabularyItems = vocabularyItems.map((vocabularyItem) => {
        return { ...vocabularyItem, id: vocabularyItem.value };
      });
      formik.setFieldValue(fieldPath, [...vocabularyItems]);
      setSelectedState(vocabularyItems);
    } else {
      let vocabularyItem = allOptions.find((o) => o.value === data.value);
      vocabularyItem = { ...vocabularyItem, id: vocabularyItem?.value };
      formik.setFieldValue(fieldPath, vocabularyItem);
      setSelectedState(vocabularyItem);
    }
  };

  const handleOpen = (e) => {
    if (e.currentTarget.classList.contains("icon")) return;
    setOpenState(true);
  };

  const handleSubmit = () => {
    const prepSelect = [
      ...selectedState.map((item) => {
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
        selectOnBlur={false}
        optimized={optimized}
        onBlur={() => setFieldTouched(fieldPath)}
        deburr
        fieldPath={fieldPath}
        multiple={multiple}
        featured={featuredOptions}
        options={serializedOptions}
        onClick={(e) => handleOpen(e)}
        onChange={handleChange}
        value={multiple ? value.map((o) => o?.id) : value?.id}
        {...uiProps}
      />
      <label className="helptext">{helpText}</label>

      {openState && (
        <TreeSelectFieldModal
          fieldPath={fieldPath}
          query={query}
          setQuery={setQuery}
          multiple={multiple}
          openState={openState}
          setOpenState={setOpenState}
          placeholder={placeholder}
          allOptions={allOptions}
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
};

VocabularyTreeSelectField.defaultProps = {
  noResultsMessage: "No results found.",
  optimized: false,
};
