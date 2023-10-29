import React from "react";
import { Button } from "semantic-ui-react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { useVocabularyApiClient } from "@js/oarepo_vocabularies";

export const PublishButton = ({ newChildItemParentId }) => {
  const { isSubmitting, createOrUpdate } =
    useVocabularyApiClient(newChildItemParentId);
  return (
    <Button
      fluid
      disabled={isSubmitting}
      loading={isSubmitting}
      color="green"
      onClick={() => createOrUpdate()}
      icon="save"
      labelPosition="left"
      content={i18next.t("save")}
      type="button"
    />
  );
};

PublishButton.propTypes = {
  newChildItemParentId: PropTypes.string,
};
