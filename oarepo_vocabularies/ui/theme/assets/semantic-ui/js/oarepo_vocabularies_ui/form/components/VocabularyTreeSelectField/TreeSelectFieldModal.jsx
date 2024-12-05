import React, { useState, useMemo } from "react";
import PropTypes from "prop-types";
import {
  Button,
  Header,
  Grid,
  Input,
  Container,
  Modal,
  ModalHeader,
  ModalContent,
  ModalActions,
} from "semantic-ui-react";
import {
  useVocabularySuggestions,
  OptionsLoadingSkeleton,
} from "@js/oarepo_vocabularies";
import {
  EmptyResultsElement,
  useConfirmationModal as useModal,
} from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _groupBy from "lodash/groupBy";
import _toPairs from "lodash/toPairs";
import _sortBy from "lodash/sortBy";
import _reject from "lodash/reject";
import { HierarchyColumn } from "./HierarchyColumn";
import {
  sortByTitle,
  isSelectable,
  suggestionsToColumnOptions,
  isColumnOptionHidden,
} from "./util";
import TreeSelectValues from "./TreeSelectValues";
import { VocabularyModalTrigger } from "../VocabularyModalTrigger";

export const TreeSelectFieldModal = ({
  multiple,
  placeholder,
  options,
  value,
  root,
  trigger,
  showLeafsOnly,
  filterFunction,
  onSubmit,
  onSelect,
  onClose,
  selected,
  loadingMessage,
  vocabularyType,
}) => {
  const { isOpen, close, open } = useModal();

  const valueAncestors =
    options.find((o) => o.value === value.id)?.hierarchy?.ancestors || [];

  const [currentAncestors, setCurrentAncestors] = useState(valueAncestors);
  const [keybState, setKeybState] = useState([]);
  const {
    suggestions: searchResults,
    loading: suggestionsLoading,
    error: suggestionsError,
    query: searchQuery,
    noResults,
    executeSearch,
  } = useVocabularySuggestions({ type: vocabularyType });

  const noSearchResults = suggestionsError || noResults;

  const _options =
    searchQuery !== ""
      ? suggestionsToColumnOptions(
          searchResults,
          root,
          showLeafsOnly,
          filterFunction
        )
      : options;
  const hierarchyLevels = _groupBy(_options, "hierarchy.ancestors.length");

  const columns = useMemo(
    () =>
      _sortBy(_toPairs(hierarchyLevels), ([index, _]) =>
        Number.parseInt(index)
      ).map(([_, column], columnIndex, _columns) =>
        sortByTitle(
          _reject(column, (option) =>
            isColumnOptionHidden(option, columnIndex, _columns)
          )
        )
      ),
    [hierarchyLevels, searchResults]
  );

  const columnsCount = columns.length;

  function _onClose () {
    close()
    setKeybState([])
    setCurrentAncestors(valueAncestors)
    onClose()
  }

  const openHierarchyNode = (parent, level) => () => {
    let updatedParents = [...currentAncestors];
    updatedParents.splice(level + 1);
    updatedParents[level] = parent;

    let updatedKeybState = [...keybState];

    const columnOptions = columns[level];
    const nextColumnIndex = columnOptions.findIndex((o) => o.value === parent);
    updatedKeybState.splice(level + 1);
    updatedKeybState[level] = nextColumnIndex;

    setCurrentAncestors(updatedParents);
    setKeybState(updatedKeybState);
  };

  const selectAndClose = (option) => {
    onSelect([option]);
    onSubmit([option]);
    close();
  };

  const selectOption = (option) => {
    const existingIndex = selected.findIndex((i) => i.value === option?.value);
    const existingParentIndex = selected.findIndex((i) =>
      option?.hierarchy.ancestors.includes(i.value)
    );
    const childIndexes = selected.reduce(
      (acc, curr, index) =>
        curr.hierarchy?.ancestors.includes(option.value)
          ? [...acc, index]
          : acc,
      []
    );

    if (existingIndex !== -1) {
      onSelect((prevState) =>
        prevState.filter((_, index) => index !== existingIndex)
      );
    } else if (multiple && selected.length !== 0) {
      onSelect((prevState) =>
        updateState(prevState, option, existingParentIndex, childIndexes)
      );
    } else {
      onSelect([option]);
    }
  };

  const handleSelect = React.useCallback(
    (option, e) => {
      e.preventDefault();
      if (!isSelectable(option)) {
        return;
      }
      if (!multiple) {
        selectAndClose(option);
      } else {
        selectOption(option);
      }
    },
    [multiple, onSubmit, selected, onSelect]
  );

  const handleSubmit = React.useCallback(() => {
    onSubmit(selected);
    close();
  }, [onSubmit, selected]);

  const updateState = (
    prevState,
    option,
    existingParentIndex,
    childIndexes
  ) => {
    let newState = [...prevState];
    newState = removeChildIndexes(newState, childIndexes);

    if (existingParentIndex !== -1 && childIndexes.length === 0) {
      newState = newState.filter((_, index) => index !== existingParentIndex);
    }
    return [...newState, option];
  };

  const removeChildIndexes = (state, childIndexes) => {
    if (childIndexes.length > 0) {
      let adjustedState = [...state];
      childIndexes.forEach((childIndex, i) => {
        adjustedState = adjustedState.filter(
          (_, index) => index !== childIndex - i
        );
      });
      return adjustedState;
    }
    return state;
  };

  const moveKey = React.useCallback(
    (index, newIndex, back = false) => {
      setKeybState((prev) => {
        const newState = [...prev];
        const newValue = back ? undefined : newIndex;
        if (back) {
          newState.splice(index, 1);
        } else {
          newState[index] = newValue;
        }
        return newState;
      });
    },
    [setKeybState]
  );

  const handleArrowUp = React.useCallback(
    (e, index, data) => {
      const newIndex = keybState[index] - 1;
      if (newIndex >= 0) {
        openHierarchyNode(data[newIndex].value, index)();
        moveKey(index, newIndex, false);
        if (e.shiftKey) {
          handleSelect(data[newIndex], e);
        }
      }
    },
    [setKeybState, openHierarchyNode, moveKey, handleSelect]
  );

  const handleArrowDown = (e, index, data) => {
    const newIndex = keybState[index] + 1;
    if (newIndex < data.length) {
      openHierarchyNode(data[newIndex].value, index)();
      moveKey(index, newIndex, false);
      if (e.shiftKey) {
        handleSelect(data[newIndex], e);
      }
    }
  };

  const handleArrowLeft = (index) => {
    if (index > 0) {
      setCurrentAncestors((prev) => {
        const newState = [...prev];
        newState.splice(index, 1);
        return newState;
      });
      moveKey(index, null, true);
    }
  };

  const handleArrowRight = (index) => {
    if (index < columnsCount - 1) {
      const nextColumnOptions = columns[index + 1];
      const nextColumnIndex = nextColumnOptions.findIndex(
        (o) => o.hierarchy.ancestors[0] === currentAncestors[index]
      );
      if (nextColumnIndex !== -1) {
        const newIndex = nextColumnIndex;
        openHierarchyNode(nextColumnOptions[newIndex].value, index + 1)();
        moveKey(index + 1, newIndex, false);
      }
    }
  };

  const handleEnterSpace = (e, index, data) => {
    handleSelect(data[keybState[index]], e);
  };

  const handleKey = React.useCallback(
    (e, index) => {
      e.preventDefault();
      index = Math.max(keybState.length - 1, index);
      const data = columns[index];

      switch (e.key) {
        case "ArrowUp":
          handleArrowUp(e, index, data);
          break;

        case "ArrowDown":
          handleArrowDown(e, index, data);
          break;

        case "ArrowLeft":
          handleArrowLeft(index);
          break;

        case "ArrowRight":
          handleArrowRight(index);
          break;

        case "Enter":
        case " ":
          handleEnterSpace(e, index, data);
          break;
      }
    },
    [columns]
  );

  return (
    <Modal
      trigger={trigger}
      open={isOpen}
      onOpen={open}
      onClose={_onClose}
      closeOnDimmerClick={false}
      className="tree-field"
    >
      <ModalHeader>
        <Grid.Row>
          <Header as="h3">{placeholder || "Choose Items"}</Header>
          <Grid.Column>
            <Input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                executeSearch(e.target.value);
              }}
              placeholder="Search..."
            />
          </Grid.Column>
        </Grid.Row>
      </ModalHeader>
      <ModalContent>
        <Grid>
          <div className="columns-container">
            <Grid columns={1}>
              <OptionsLoadingSkeleton
                  loading={suggestionsLoading}
                  loadingMessage={loadingMessage}
              />
              {noSearchResults && (
                <Grid.Column stretched>
                  <EmptyResultsElement
                    queryString={searchQuery}
                    resetQuery={() => executeSearch("")}
                    extraContent=""
                  />
                </Grid.Column>
              )}
              {!suggestionsLoading && !noSearchResults && (
                <Container>
                  {columns.map((items, level) => (
                    <HierarchyColumn
                      items={items}
                      key={level}
                      level={level}
                      onSelect={handleSelect}
                      onExpand={openHierarchyNode}
                      onKeyDown={handleKey}
                      selected={selected}
                      currentAncestors={currentAncestors}
                      value={value}
                      multiple={multiple}
                      isLast={level < columnsCount - 1}
                    />
                  ))}
                </Container>
              )}
            </Grid>
          </div>
        </Grid>
      </ModalContent>
      {multiple && (
        <ModalActions>
          <Grid.Row className="gapped">
            <TreeSelectValues selected={selected} onRemove={handleSelect} />
            <Button
              content={i18next.t("Confirm")}
              labelPosition="right"
              floated="right"
              icon="checkmark"
              onClick={handleSubmit}
              secondary
            />
          </Grid.Row>
        </ModalActions>
      )}
    </Modal>
  );
};

TreeSelectFieldModal.propTypes = {
  multiple: PropTypes.bool,
  placeholder: PropTypes.string,
  options: PropTypes.array.isRequired,
  value: PropTypes.oneOfType([PropTypes.array, PropTypes.object]).isRequired,
  onSubmit: PropTypes.func.isRequired,
  selected: PropTypes.array.isRequired,
  onSelect: PropTypes.func.isRequired,
  onClose: PropTypes.func,
  vocabularyType: PropTypes.string.isRequired,
  trigger: PropTypes.node,
  root: PropTypes.string,
  showLeafsOnly: PropTypes.bool,
  filterFunction: PropTypes.func,
  loadingMessage: PropTypes.string,
};

TreeSelectFieldModal.defaultProps = {
  loadingMessage: i18next.t("Loading..."),
  trigger: <VocabularyModalTrigger />,
};
