import * as React from "react";
import { Button, Icon, Modal } from "semantic-ui-react";
import { useConfirmationModal as useModal } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _capitalize from "lodash/capitalize";
import PropTypes from "prop-types";
import { VocabularyRemoteSearchAppLayout } from "./VocabularyRemoteSearchAppLayout";
import VocabularyAddItemForm from "./VocabularyAddItemForm";
import { ModalActions } from "./constants";

export const VocabularyRemoteSelectModal = ({
  vocabulary,
  trigger,
  value,
  addItem,
  removeItem,
  label,
  overriddenComponents,
  multiple = false,
  initialAction = ModalActions.SEARCH,
}) => {
  const { isOpen, close, open } = useModal();
  const [action, setAction] = React.useState(initialAction);

  const inSearchMode = action === ModalActions.SEARCH;
  const inAddMode = action === ModalActions.ADD;

  const addNew = React.useCallback(() => {
    setAction(ModalActions.ADD);
  });

  const backToSearch = React.useCallback(() => {
    setAction(ModalActions.SEARCH);
  });

  const handleSelect = React.useCallback((value) => {
    if (!multiple) {
      close();
    }
    addItem(value);
  });

  const handleNewItem = React.useCallback((value) => {
    close();
    addItem(value);
  });

  const handleSubmit = () => {
    close();
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
        {inSearchMode && (
          <VocabularyRemoteSearchAppLayout
            overriddenComponents={overriddenComponents}
            multiple={multiple}
            vocabulary={vocabulary}
            handleSelect={handleSelect}
            addNew={addNew}
            onSubmit={handleSubmit}
          />
        )}
        {inAddMode && (
          <VocabularyAddItemForm
            overriddenComponents={overriddenComponents}
            backToSearch={backToSearch}
            onSubmit={handleNewItem}
          />
        )}
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
  addItem: PropTypes.func.isRequired,
  removeItem: PropTypes.func.isRequired,
  overriddenComponents: PropTypes.object,
};

VocabularyRemoteSelectModal.defaultProps = {
  initialAction: ModalActions.SEARCH,
  label: i18next.t("item"),
  multiple: false,
  overriddenComponents: {},
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
