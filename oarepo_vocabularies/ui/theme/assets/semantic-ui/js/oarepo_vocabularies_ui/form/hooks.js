import { useDepositApiClient } from "@js/oarepo_ui";
import _isEmpty from "lodash/isEmpty";

export const useVocabularyApiClient = (newChildItemParentId) => {
  const { apiClient, createUrl, formik } = useDepositApiClient();
  const {
    isSubmitting,
    values,
    validateForm,
    setSubmitting,
    setFieldError,
    setFieldValue,
    read,
  } = formik;

  async function createOrUpdate() {
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
        setFieldValue(
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
