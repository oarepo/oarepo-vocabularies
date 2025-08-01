import {
  DRAFT_HAS_VALIDATION_ERRORS,
  DRAFT_SAVE_FAILED,
  DRAFT_SAVE_STARTED,
  DRAFT_SAVE_SUCCEEDED,
} from "@js/invenio_rdm_records/src/deposit/state/types";

export const createOrUpdate = ({
  draft,
  newChildItemParentId,
  successMessage = "Vocabulary item saved successfully",
  ...saveArgs
}) => {
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

      dispatch({
        type: DRAFT_SAVE_SUCCEEDED,
        payload: { data: response.data, formFeedbackMessage: successMessage },
      });
      window.location.href = response.data.links.self_html;
      return response;
    } catch (error) {
      console.error("Draft save failed:", error);
      dispatch({
        type: DRAFT_SAVE_FAILED,
        payload: { error },
      });
      throw error;
    }
  };
};
