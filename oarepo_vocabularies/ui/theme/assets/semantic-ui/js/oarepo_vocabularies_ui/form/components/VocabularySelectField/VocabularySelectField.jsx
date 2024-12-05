import React from "react";
import { RelatedSelectField } from "@js/oarepo_ui";
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
  ...restProps
}) => {
  const suggestionsConfig = {
    suggestionAPIUrl: `/api/vocabularies/${type}`,
  };
  if (externalAuthority) {
    suggestionsConfig.externalSuggestionApi = `${suggestionsConfig.suggestionAPIUrl}/authoritative`;
  }

  function _serializeSuggestions(suggestions) {
    // We need to do post-filtering here (it seems impossible to add pre-filter to suggestion API query)
    return serializeVocabularySuggestions(suggestions).filter(opt => filterFunction(opt));
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
};

VocabularySelectField.defaultProps = {
  multiple: false,
  externalAuthority: false,
  suggestionAPIHeaders: {
    // TODO: remove after #BE-96 gets resolved
    Accept: "application/json",
  },
  filterFunction: opt => opt,
};
