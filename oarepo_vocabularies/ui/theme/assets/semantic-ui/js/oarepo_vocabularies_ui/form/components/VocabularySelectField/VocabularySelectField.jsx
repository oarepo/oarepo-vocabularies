import React from "react";
import { RelatedSelectField, useFieldData } from "@js/oarepo_ui/forms";
import { serializeVocabularySuggestions } from "@js/oarepo_vocabularies";
import PropTypes from "prop-types";

// for adding free text items
const serializeAddedValue = (value) => {
  return { text: value, value, key: value, name: value, id: value };
};

export const VocabularySelectField = ({
  type,
  fieldPath,
  externalAuthority,
  multiple,
  filterFunction,
  icon,
  label,
  required,
  helpText,
  placeholder,
  fieldRepresentation,
  ...restProps
}) => {
  const suggestionsConfig = {
    suggestionAPIUrl: `/api/vocabularies/${type}`,
  };
  if (externalAuthority) {
    suggestionsConfig.externalSuggestionApi = `${suggestionsConfig.suggestionAPIUrl}/authoritative`;
  }

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

  function _serializeSuggestions(suggestions) {
    // We need to do post-filtering here (it seems impossible to add pre-filter to suggestion API query)
    return serializeVocabularySuggestions(suggestions).filter((opt) =>
      filterFunction(opt)
    );
  }

  return (
    <RelatedSelectField
      fieldPath={fieldPath}
      {...suggestionsConfig}
      selectOnBlur={false}
      serializeSuggestions={_serializeSuggestions}
      multiple={multiple}
      deburr
      serializeAddedValue={serializeAddedValue}
      {...fieldData}
      {...restProps}
    />
  );
};

VocabularySelectField.propTypes = {
  type: PropTypes.string.isRequired,
  fieldPath: PropTypes.string.isRequired,
  externalAuthority: PropTypes.bool,
  multiple: PropTypes.bool,
  filterFunction: PropTypes.func,
  icon: PropTypes.string,
  label: PropTypes.oneOfType([PropTypes.string, PropTypes.node]),
  required: PropTypes.bool,
  helpText: PropTypes.string,
  placeholder: PropTypes.string,
  fieldRepresentation: PropTypes.string,
};

VocabularySelectField.defaultProps = {
  multiple: false,
  externalAuthority: false,
  filterFunction: (opt) => opt,
};
