import React from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { connect } from "react-redux";
import { createOrUpdate } from "../../state/deposit/actions";
import { DRAFT_SAVE_STARTED } from "@js/invenio_rdm_records/src/deposit/state/types";
import { useDepositFormAction } from "@js/oarepo_ui/forms";
import PropTypes from "prop-types";

const PublishButtonComponent = React.memo(
  ({ publishAction, actionState, newChildItemParentId, ...uiProps }) => {
    const { handleAction: handlePublish, isSubmitting } = useDepositFormAction({
      action: publishAction,
      params: { newChildItemParentId },
    });
    return (
      <Button
        fluid
        disabled={isSubmitting}
        loading={isSubmitting && actionState === DRAFT_SAVE_STARTED}
        color="green"
        onClick={() => handlePublish()}
        icon="save"
        labelPosition="left"
        content={i18next.t("save")}
        type="button"
        {...uiProps}
      />
    );
  }
);

PublishButtonComponent.displayName = "PublishButtonComponent";

PublishButtonComponent.propTypes = {
  publishAction: PropTypes.func.isRequired,
  actionState: PropTypes.string.isRequired,
  newChildItemParentId: PropTypes.string,
};

const mapDispatchToProps = (dispatch) => ({
  publishAction: (values, params) => dispatch(createOrUpdate(values, params)),
});

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
});

export const PublishButton = connect(
  mapStateToProps,
  mapDispatchToProps
)(PublishButtonComponent);

PublishButton.displayName = "PublishButton";

export default PublishButton;
