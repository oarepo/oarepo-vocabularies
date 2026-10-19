// SPDX-FileCopyrightText: 2025-2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

import {
  DRAFT_SAVE_FAILED,
  DRAFT_SAVE_STARTED,
  DRAFT_SAVE_SUCCEEDED,
} from "@js/invenio_rdm_records/src/deposit/state/types";
import { SET_VALIDATION_ERRORS } from "@js/oarepo_ui/forms/state/deposit/types";
import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const createOrUpdate = (
  draft,
  {
    newChildItemParentId,
    successMessage = i18next.t(
      "Vocabulary item saved successfully. Redirecting..."
    ),
    errorMessage = i18next.t("Error saving vocabulary item"),
  }
) => {
  return async (dispatch, getState, config) => {
    dispatch({
      type: DRAFT_SAVE_STARTED,
    });
    const recordId = draft.id || crypto.randomUUID();
    const draftWithUUID = { ...draft, id: recordId };

    let draftToSave;
    if (newChildItemParentId) {
      draftToSave = {
        ...draftWithUUID,
        hierarchy: { parent: newChildItemParentId },
      };
    } else {
      draftToSave = draftWithUUID;
    }

    let response;

    try {
      if (config?.config?.createUrl) {
        response = await config.service.drafts.create(draftToSave);
      } else {
        response = await config.apiClient.saveDraft(
          draftToSave,
          draftToSave.links
        );
      }
      window.location.href = response.data.links.self_html;

      dispatch({
        type: DRAFT_SAVE_SUCCEEDED,
        payload: { data: response.data, formFeedbackMessage: successMessage },
      });
      return response;
    } catch (error) {
      console.error("Draft save failed:", error);
      // the api client throws field errors already deserialized (e.g. {mappings: [...]}),
      // any other failure carries the raw backend response ({status, message})
      if (!_isEmpty(error?.errors) && !error.errors.status) {
        dispatch({
          type: SET_VALIDATION_ERRORS,
          payload: {
            errors: error.errors,
            formFeedbackMessage: i18next.t(
              "Vocabulary item could not be saved due to validation errors: "
            ),
          },
        });
      } else {
        dispatch({
          type: DRAFT_SAVE_FAILED,
          payload: {
            error,
            formFeedbackMessage: i18next.t(
              error?.errors?.message ?? errorMessage
            ),
          },
        });
      }
      throw error;
    }
  };
};
