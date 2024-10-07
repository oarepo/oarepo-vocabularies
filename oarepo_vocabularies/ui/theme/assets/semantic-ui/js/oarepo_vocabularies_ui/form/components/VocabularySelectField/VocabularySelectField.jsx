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
  ...restProps
}) => {
  const suggestionsConfig = {
    suggestionAPIUrl: `/api/vocabularies/${type}`,
  };
  if (externalAuthority) {
    suggestionsConfig.externalSuggestionApi = `${suggestionsConfig.suggestionAPIUrl}/authoritative`;
  }
  return (
    <RelatedSelectField
      fieldPath={fieldPath}
      {...suggestionsConfig}
      selectOnBlur={false}
      serializeSuggestions={serializeVocabularySuggestions}
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
};

VocabularySelectField.defaultProps = {
  multiple: false,
  externalAuthority: false,
  suggestionAPIHeaders: {
    // TODO: remove after #BE-96 gets resolved
    Accept: "application/json",
  },
};
