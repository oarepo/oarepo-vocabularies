import { useDepositApiClient } from "@js/oarepo_ui";
import { useFormikContext } from "formik";
import _isEmpty from "lodash/isEmpty";

export const useVocabularyApiClient = (newChildItemParentId) => {
  const { apiClient, createUrl } = useDepositApiClient();
  // TODO: maybe - as useDepositApiClient is already calling formik, it could makse sense for it to pass
  // entire formik object down to any users, however, this might be a bit tricky,
  // because I destructure some properties in the useDepositApiClient, so I would have to return
  // those explicitly from the useDepositApiClient which would become a bit cluttered
  const {
    isSubmitting,
    values,
    validateForm,
    setSubmitting,
    setFieldError,
    setFieldValue,
  } = useFormikContext();

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

      // TODO should return self_html link similarly like in deposits?
      window.location.href = response.links.self.replace("/api", "");

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

  return { values, isSubmitting, createOrUpdate };
};
