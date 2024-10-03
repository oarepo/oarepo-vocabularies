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
import { useVocabularySuggestions } from "@js/oarepo_vocabularies";
import { EmptyResultsElement } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _groupBy from "lodash/groupBy";
import _toPairs from "lodash/toPairs";
import _sortBy from "lodash/sortBy";
import _reject from "lodash/reject";

import { OptionsLoadingSkeleton } from "./OptionsLoadingSkeleton";
import { HierarchyColumn } from "./HierarchyColumn";
import {
  sortByTitle,
  isSelectable,
  isDescendant,
  suggestionsToColumnOptions,
} from "./util";
import TreeSelectValues from "./TreeSelectValues";

export const TreeSelectFieldModal = ({
  multiple,
  placeholder,
  openState,
  onOpen,
  onClose,
  options,
  value,
  root,
  showLeafsOnly,
  filterFunction,
  handleSubmit,
  selectedState,
  setSelectedState,
  loadingMessage,
  vocabularyType,
}) => {
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
          _reject(
            column,
            (option) =>
              !isSelectable(option) &&
              (option.element_type === "leaf" ||
                (option.element_type === "parent" &&
                  (columnIndex < _columns.length - 1
                    ? !_columns[columnIndex + 1][1].some((child) =>
                        isDescendant(child, option.value)
                      )
                    : true)))
          )
        )
      ),
    [hierarchyLevels, searchResults]
  );

  const columnsCount = columns.length;

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

  const handleSelect = React.useCallback(
    (option, e) => {
      e.preventDefault();
      if (!isSelectable(option)) {
        return;
      }
      if (!multiple) {
        setSelectedState([option]);
        handleSubmit([option]);
      } else {
        const existingIndex = selectedState.findIndex(
          (i) => i.value === option?.value
        );
        const existingParentIndex = selectedState.findIndex((i) =>
          option?.hierarchy.ancestors.includes(i.value)
        );
        const childIndexes = selectedState.reduce(
          (acc, curr, index) =>
            curr.hierarchy?.ancestors.includes(option.value)
              ? [...acc, index]
              : acc,
          []
        );

        if (existingIndex !== -1) {
          setSelectedState((prevState) =>
            prevState.filter((_, index) => index !== existingIndex)
          );
        } else if (multiple && selectedState.length !== 0) {
          setSelectedState((prevState) =>
            updateState(prevState, option, existingParentIndex, childIndexes)
          );
        } else {
          setSelectedState([option]);
        }
      }
    },
    [multiple, handleSubmit, selectedState, setSelectedState]
  );

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
      onClose={onClose}
      onOpen={onOpen}
      open={openState}
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
              {suggestionsLoading && (
                <OptionsLoadingSkeleton loadingMessage={loadingMessage} />
              )}
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
                      selected={selectedState}
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
            <TreeSelectValues
              selected={selectedState}
              onRemove={handleSelect}
            />
            <Button
              content={i18next.t("Confirm")}
              labelPosition="right"
              floated="right"
              icon="checkmark"
              onClick={() => handleSubmit(selectedState)}
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
  openState: PropTypes.bool.isRequired,
  onOpen: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired,
  options: PropTypes.array.isRequired,
  value: PropTypes.oneOfType([PropTypes.array, PropTypes.object]).isRequired,
  handleSubmit: PropTypes.func.isRequired,
  selectedState: PropTypes.array.isRequired,
  setSelectedState: PropTypes.func.isRequired,
  vocabularyType: PropTypes.string.isRequired,
  root: PropTypes.string,
  showLeafsOnly: PropTypes.bool,
  filterFunction: PropTypes.func,
  loadingMessage: PropTypes.string,
  noResultsMessage: PropTypes.string,
};

TreeSelectFieldModal.defaultProps = {
  noResultsMessage: i18next.t("No results found"),
  loadingMessage: i18next.t("Loading..."),
};
