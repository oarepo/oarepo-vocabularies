import * as React from "react";
import { useSuggestionApi } from "@js/oarepo_ui";
import { serializeVocabularySuggestions } from "@js/oarepo_vocabularies";
import { VocabularyModalTrigger } from "./components/VocabularyModalTrigger";
import _isEmpty from "lodash/isEmpty";
import _isObject from "lodash/isObject";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const useVocabularySuggestions = ({ type, ...rest }) => {
  return useSuggestionApi({
    suggestionAPIUrl: `/api/vocabularies/${type}`,
    serializeSuggestions: serializeVocabularySuggestions,
    ...rest,
  });
};

export const useModalTrigger = ({
  value,
  defaultLabel = i18next.t("Choose item"),
  editLabel = i18next.t("Edit"),
  trigger,
}) => {
  // We need to check both for pure empty values and empty (initial) values for
  // vocabulary items here.
  const _valueEmpty = _isEmpty(value) || (_isObject(value) && value._id === "");

  return trigger ?? !_valueEmpty ? (
    <VocabularyModalTrigger icon="pencil" label={editLabel} />
  ) : (
    <VocabularyModalTrigger label={defaultLabel} />
  );
};
