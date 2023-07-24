import React from "react";
import PropTypes from "prop-types";
import { SelectField } from "react-invenio-forms";
import { useFormikContext, getIn } from "formik";

export const SelectInputField = ({
  clearable,
  fieldPath,
  label,
  optimized,
  options,
  required,
  width,
  currentlySelectedLanguages,
}) => {
  console.log(options);
  const { values } = useFormikContext();
  const currentlySelectedLanguage = getIn(values, fieldPath, "");
  const filteredLanguageOptions = options.filter(
    (language) =>
      currentlySelectedLanguages[0].language !== language.value ||
      currentlySelectedLanguage === language.value
  );
  console.log(currentlySelectedLanguages, options, currentlySelectedLanguage);
  return (
    <SelectField
      clearable={clearable}
      fieldPath={fieldPath}
      label={label}
      optimized={optimized}
      options={filteredLanguageOptions}
      required={required}
      width={width}
    />
  );
};

SelectInputField.propTypes = {
  clearable: PropTypes.bool,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  optimized: PropTypes.bool,
  options: PropTypes.array.isRequired, // Assuming options is an object with the 'languages' property
  required: PropTypes.bool,
  width: PropTypes.number,
};
