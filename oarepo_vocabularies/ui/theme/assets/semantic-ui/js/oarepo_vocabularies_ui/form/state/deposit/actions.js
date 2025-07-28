import {
  DRAFT_DELETE_FAILED,
  DRAFT_DELETE_STARTED,
  DRAFT_HAS_VALIDATION_ERRORS,
  DRAFT_PREVIEW_FAILED,
  DRAFT_PREVIEW_STARTED,
  DRAFT_SAVE_FAILED,
  DRAFT_SAVE_STARTED,
  DRAFT_SAVE_SUCCEEDED,
  SET_COMMUNITY,
} from "@js/invenio_rdm_records/src/deposit/state/types";

export const createOrUpdate = ({
  draft,
  newChildItemParentId,
  successMessage = "Vocabulary item saved successfully",
  ...saveArgs
}) => {
  return async (dispatch, getState, config) => {
    console.log(config, "config");

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

      console.log(draftToSave, "draftToSave");

      dispatch({
        type: DRAFT_SAVE_SUCCEEDED,
        payload: { data: response.data, formFeedbackMessage: successMessage },
      });
      
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
