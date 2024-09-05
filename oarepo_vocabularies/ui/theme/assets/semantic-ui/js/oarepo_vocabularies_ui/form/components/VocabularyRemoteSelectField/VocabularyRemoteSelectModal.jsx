import * as React from "react";
import { Button, Icon, Modal } from "semantic-ui-react";
import { useConfirmationModal as useModal } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _capitalize from "lodash/capitalize";
import PropTypes from "prop-types";
import { VocabularyRemoteSearchAppLayout } from "./VocabularyRemoteSearchAppLayout";
import { ModalActions } from "./constants";

export const VocabularyRemoteSelectModal = ({
  vocabulary,
  trigger,
  onChange = () => {},
  label,
  value,
  multiple = false,
  initialAction = ModalActions.SEARCH,
}) => {
  const { isOpen, close, open } = useModal();
  const [action, setAction] = React.useState(initialAction);

  const inSearchMode = action === ModalActions.SEARCH;
  const inAddMode = action === ModalActions.ADD;

  const handleAddNew = () => {
    setAction(ModalActions.ADD);
  };

  const handleSelect = React.useCallback((value) => {
    if (!multiple) {
      return handleSubmit(value);
    } else {
    }
  });

  const handleSubmit = (values) => {
    // We have to close the modal first because onChange and passing
    // values as an object makes React get rid of this component. Otherwise
    // we get a memory leak warning.
    close();
    onChange(values);
  };

  return (
    <Modal
      onOpen={() => open()}
      open={isOpen}
      trigger={trigger}
      onClose={() => {
        close();
      }}
      closeIcon
      closeOnDimmerClick={false}
    >
      <>
        <Modal.Header as="h2" className="pt-10 pb-10">
          {_capitalize(action)} {label}
        </Modal.Header>
        <Modal.Content>
          {inSearchMode && (
            <VocabularyRemoteSearchAppLayout
              vocabulary={vocabulary}
              handleSelect={handleSelect}
            />
          )}
          {inAddMode && <h1>Add new item</h1>}
        </Modal.Content>
        <Modal.Actions>
          {!inAddMode && (
            <Button
              icon="plus"
              content={i18next.t("Add new")}
              onClick={() => handleAddNew()}
            />
          )}
          {!inSearchMode && (
            <Button
              icon="arrow left"
              content={i18next.t("Back to search")}
              onClick={() => setAction(ModalActions.SEARCH)}
            />
          )}
          {(multiple || inAddMode) && (
            <Button
              content={i18next.t("Confirm")}
              icon="checkmark"
              onClick={() => handleSubmit()}
              secondary
            />
          )}
        </Modal.Actions>
      </>
    </Modal>
  );
};

VocabularyRemoteSelectModal.propTypes = {
  trigger: PropTypes.object.isRequired,
  onChange: PropTypes.func,
  label: PropTypes.string,
  multiple: PropTypes.bool,
  initialAction: PropTypes.string,
  value: PropTypes.oneOf([PropTypes.object, PropTypes.array]),
  vocabulary: PropTypes.string.isRequired,
};

VocabularyRemoteSelectModal.defaultProps = {
  initialAction: ModalActions.SEARCH,
  label: i18next.t("item"),
  multiple: false,
  onChange: () => {},
  trigger: (
    <Button
      className="array-field-add-button"
      type="button"
      icon
      labelPosition="left"
    >
      <Icon name="add" />
      {i18next.t("Choose item")}
    </Button>
  ),
};
export default VocabularyRemoteSelectModal;
