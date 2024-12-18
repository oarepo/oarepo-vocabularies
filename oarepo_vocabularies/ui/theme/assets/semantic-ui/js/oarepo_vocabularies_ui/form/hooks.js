import * as React from "react";
import { useDepositApiClient, useSuggestionApi } from "@js/oarepo_ui";
import { serializeVocabularySuggestions } from "@js/oarepo_vocabularies";
import { VocabularyModalTrigger } from "./components/VocabularyModalTrigger";
import _isEmpty from "lodash/isEmpty";
import _isObject from "lodash/isObject";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const useVocabularyApiClient = (newChildItemParentId) => {
  const { apiClient, createUrl, formik } = useDepositApiClient();
  const {
    isSubmitting,
    values,
    validateForm,
    setSubmitting,
    setFieldError,
    read,
  } = formik;

  async function createOrUpdate () {
    const validationErrors = await validateForm();
    if (!_isEmpty(validationErrors)) return;
    setSubmitting(true);
    let response;
    // unfortunately, not possible to use saveOrCreate as vocabularies have a different principle
    // where user is expected to provide ID when creating new vocabulary item (vs records where id is created by the server)
    try {
      if (createUrl) {
        if (newChildItemParentId) {
          response = await apiClient.createDraft({
            ...values,
            hierarchy: { parent: newChildItemParentId },
          });
        } else {
          response = await apiClient.createDraft(values);
        }
      } else {
        response = await apiClient.saveDraft(values);
      }

      window.location.href = response.links.self_html;

      return response;
    } catch (error) {
      if (
        error &&
        error.status === 400 &&
        error.message === "A validation error occurred."
      ) {
        error.errors?.forEach((err) =>
          setFieldError(err.field, err.messages.join(" "))
        );
      } else {
        setFieldError(
          "httpErrors",
          error?.response?.data?.message ?? error.message
        );
      }

      return false;
    } finally {
      setSubmitting(false);
    }
  }

  return { values, isSubmitting, createOrUpdate, formik, read };
};

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
