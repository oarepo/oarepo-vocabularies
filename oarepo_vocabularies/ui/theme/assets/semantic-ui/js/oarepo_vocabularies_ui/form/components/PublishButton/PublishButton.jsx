import React from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { connect } from "react-redux";
import { useFormikContext } from "formik";
import { createOrUpdate } from "../../state/deposit/actions";
import { DRAFT_SAVE_STARTED } from "@js/invenio_rdm_records/src/deposit/state/types";

const PublishButtonComponent = React.memo(
  ({ publishAction, actionState, newChildItemParentId, ...uiProps }) => {
    const { values, setSubmitting, isSubmitting } = useFormikContext();
    const handlePublish = () => {
      setSubmitting(true);
      publishAction({ draft: values, newChildItemParentId }).finally(() => {
        setSubmitting(false);
      });
    };
    return (
      <Button
        fluid
        disabled={isSubmitting}
        loading={isSubmitting && actionState === DRAFT_SAVE_STARTED}
        color="green"
        onClick={handlePublish}
        icon="save"
        labelPosition="left"
        content={i18next.t("save")}
        type="submit"
        {...uiProps}
      />
    );
  }
);

const mapDispatchToProps = (dispatch) => ({
  publishAction: (values) => dispatch(createOrUpdate(values)),
});

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
});

export const PublishButton = connect(
  mapStateToProps,
  mapDispatchToProps
)(PublishButtonComponent);

export default PublishButton;
