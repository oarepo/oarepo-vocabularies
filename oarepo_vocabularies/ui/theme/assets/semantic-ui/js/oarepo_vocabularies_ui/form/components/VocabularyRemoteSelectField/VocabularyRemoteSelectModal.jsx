import * as React from "react";
import { Modal, Grid, Form, Label } from "semantic-ui-react";
import { useConfirmationModal as useModal } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _capitalize from "lodash/capitalize";
import PropTypes from "prop-types";
import { VocabularyRemoteSearchAppLayout } from "./VocabularyRemoteSearchAppLayout";
import VocabularyAddItemForm from "./VocabularyAddItemForm";
import { ModalActions } from "./constants";
import { SelectedVocabularyValues } from "../SelectedVocabularyValues";
import { useFieldValue } from "./context";
import { VocabularyModalTrigger } from "../VocabularyModalTrigger";
import { useFormikContext, getIn } from "formik";

export const VocabularyRemoteSelectModal = ({
  vocabulary,
  trigger,
  label,
  overriddenComponents,
  initialAction = ModalActions.SEARCH,
  fieldPath,
  allowAdditions,
  ...rest
}) => {
  const { isOpen, close, open } = useModal();
  const { multiple, addValue, removeValue } = useFieldValue();
  const [action, setAction] = React.useState(initialAction);
  const { errors } = useFormikContext();
  const fieldError = getIn(errors, fieldPath, null);

  const inSearchMode = action === ModalActions.SEARCH;
  const inAddMode = action === ModalActions.ADD;

  const addNew = React.useCallback(() => {
    window.open(`/vocabularies/${vocabulary}/_new`, "_blank").focus();
    // setAction(ModalActions.ADD);
  });

  const backToSearch = React.useCallback(() => {
    setAction(ModalActions.SEARCH);
  });

  const handleSelect = React.useCallback(
    (value, selected) => {
      if (!multiple) {
        close();
      }
      if (!selected) {
        addValue(value);
      } else {
        removeValue(value);
      }
    },
    [multiple, addValue, removeValue]
  );

  const handleNewItem = React.useCallback((value) => {
    close();
    addValue(value);
  });

  const handleSubmit = () => {
    close();
  };

  return (
    <Form.Field>
      <Modal
        onOpen={() => open()}
        open={isOpen}
        trigger={trigger}
        onClose={() => {
          close();
        }}
        closeIcon
        closeOnDimmerClick={true}
        {...rest}
      >
        <>
          <Modal.Header as="h2" className="pt-10 pb-10">
            {_capitalize(label)}
          </Modal.Header>
          {inSearchMode && (
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
          )}
          {/* TODO: implement this with full custom fields support. */}
          {/*{inAddMode && (*/}
          {/*  <VocabularyAddItemForm*/}
          {/*    overriddenComponents={overriddenComponents}*/}
          {/*    backToSearch={backToSearch}*/}
          {/*    onSubmit={handleNewItem}*/}
          {/*  />*/}
          {/*)}*/}
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

VocabularyRemoteSelectModal.propTypes = {
  trigger: PropTypes.object,
  label: PropTypes.string,
  initialAction: PropTypes.string,
  vocabulary: PropTypes.string.isRequired,
  overriddenComponents: PropTypes.object,
  fieldPath: PropTypes.string.isRequired,
  allowAdditions: PropTypes.bool
};

VocabularyRemoteSelectModal.defaultProps = {
  initialAction: ModalActions.SEARCH,
  label: i18next.t("item"),
  overriddenComponents: {},
  trigger: <VocabularyModalTrigger />,
  allowAdditions: true,
};
export default VocabularyRemoteSelectModal;
