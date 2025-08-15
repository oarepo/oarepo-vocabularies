import * as React from "react";
import { Modal, Grid, Form, Label } from "semantic-ui-react";
import { useConfirmationModal as useModal } from "@js/oarepo_ui/forms/hooks";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _capitalize from "lodash/capitalize";
import PropTypes from "prop-types";
import { VocabularyRemoteSearchAppLayout } from "./VocabularyRemoteSearchAppLayout";
import { SelectedVocabularyValues } from "../SelectedVocabularyValues";
import { useFieldValue } from "./context";
import { useFormikContext, getIn } from "formik";
import { useModalTrigger } from "../../hooks";

export const VocabularyRemoteSelectModal = ({
  vocabulary,
  trigger,
  triggerLabel,
  label = i18next.t("item"),
  overriddenComponents = {},
  fieldPath,
  allowAdditions = true,
  ...rest
}) => {
  const { isOpen, close, open } = useModal();
  const { multiple, addValue, removeValue, value } = useFieldValue();
  const { errors } = useFormikContext();
  const _trigger = useModalTrigger({
    value,
    defaultLabel: triggerLabel,
    trigger,
  });
  const fieldError = getIn(errors, fieldPath, null);

  const addNew = () => {
    window.open(`/vocabularies/${vocabulary}/_new`, "_blank").focus();
  };

  const handleSelect = (value, selected) => {
    if (!multiple) {
      close();
    }
    if (!selected) {
      addValue(value);
    } else {
      removeValue(value);
    }
  };

  const handleSubmit = () => {
    close();
  };

  return (
    <Form.Field>
      <Modal
        onOpen={() => open()}
        open={isOpen}
        trigger={_trigger}
        onClose={() => {
          close();
        }}
        closeIcon
        closeOnDimmerClick
        {...rest}
      >
        <>
          <Modal.Header as="h2" className="pt-10 pb-10">
            {_capitalize(label)}
          </Modal.Header>
          <VocabularyRemoteSearchAppLayout
            allowAdditions={allowAdditions}
            overriddenComponents={overriddenComponents}
            vocabulary={vocabulary}
            handleSelect={handleSelect}
            addNew={addNew}
            onSubmit={handleSubmit}
            extraActions={
              multiple && (
                <Grid.Column className="rel-mb-1" floated="left">
                  <SelectedVocabularyValues />
                </Grid.Column>
              )
            }
          />
        </>
      </Modal>
      {fieldError && typeof fieldError == "string" && (
        <Label className="inline" pointing="left" prompt>
          {fieldError}
        </Label>
      )}
    </Form.Field>
  );
};
/* eslint-disable react/require-default-props */
VocabularyRemoteSelectModal.propTypes = {
  vocabulary: PropTypes.string.isRequired,
  trigger: PropTypes.node,
  triggerLabel: PropTypes.string,
  label: PropTypes.string,
  overriddenComponents: PropTypes.object,
  fieldPath: PropTypes.string.isRequired,
  allowAdditions: PropTypes.bool,
};
/* eslint-enable react/require-default-props */

export default VocabularyRemoteSelectModal;
