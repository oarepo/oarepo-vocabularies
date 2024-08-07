import React, { useMemo, useState } from "react";
import PropTypes from "prop-types";
import {
  Breadcrumb,
  Button,
  Header,
  Grid,
  Input,
  Icon,
  Checkbox,
  Label,
  Container,
  Modal,
  ModalHeader,
  ModalContent,
  ModalActions,
  List,
} from "semantic-ui-react";
import { processVocabularyItems } from "@js/oarepo_vocabularies";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _has from "lodash/has";
import _groupBy from "lodash/groupBy";
import _toPairs from "lodash/toPairs";
import _sortBy from "lodash/sortBy";
import _reject from "lodash/reject";
import _deburr from "lodash/deburr";

const isSelectable = (option) => {
  return _has(option, "selectable") ? !!option.selectable : true;
};

const isDescendant = (option, ancestorId) => {
  return option.hierarchy.ancestors.includes(ancestorId);
};

const sortByTitle = (options) =>
  options.sort((a, b) => {
    const titleComparison = a.hierarchy.ancestors?.[0]?.localeCompare(
      b.hierarchy.ancestors[0],
      i18next.language,
      { sensitivity: "base" }
    );
    if (titleComparison !== 0) {
      return titleComparison;
    } else {
      return a.hierarchy.title[0].localeCompare(
        b.hierarchy.title[0],
        i18next.language,
        { sensitivity: "base" }
      );
    }
  });

export const TreeSelectFieldModal = ({
  multiple,
  placeholder,
  root,
  openState,
  setOpenState,
  allOptions,
  value,
  handleSubmit,
  selectedState,
  setSelectedState,
}) => {
  const [query, setQuery] = useState("");
  const serializedOptions = useMemo(
    () =>
      processVocabularyItems(
        root
          ? allOptions.filter((option) => isDescendant(option, root))
          : allOptions
      ),
    [allOptions]
  );
  const valueAncestors =
    serializedOptions.find((o) => o.value === value.id)?.hierarchy?.ancestors ||
    [];
  const [parentsState, setParentsState] = useState(valueAncestors);
  const [keybState, setKeybState] = useState([]);

  const columnGroups = _groupBy(
    serializedOptions.filter(
      (o) =>
        query === "" ||
        _deburr(o.hierarchy.title[0].toLowerCase()).includes(
          _deburr(query.toLowerCase())
        )
    ),
    "hierarchy.ancestors.length"
  );

  const columns = _sortBy(_toPairs(columnGroups), ([index, _]) =>
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
  );

  const columnsCount = columns.length;

  const openHierarchyNode = (parent, level) => () => {
    let updatedParents = [...parentsState];
    updatedParents.splice(level + 1);
    updatedParents[level] = parent;

    let updatedKeybState = [...keybState];

    const columnOptions = columns[level];
    const nextColumnIndex = columnOptions.findIndex((o) => o.value === parent);
    updatedKeybState.splice(level + 1);
    updatedKeybState[level] = nextColumnIndex;

    setParentsState(updatedParents);
    setKeybState(updatedKeybState);
  };
  const handleSelect = (option, e) => {
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
  };

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

  const moveKey = (index, newIndex, back = false) => {
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
  };

  const handleArrowUp = (e, index, data) => {
    const newIndex = keybState[index] - 1;
    if (newIndex >= 0) {
      openHierarchyNode(data[newIndex].value, index)();
      moveKey(index, newIndex, false);
      if (e.shiftKey) {
        handleSelect(data[newIndex], e);
      }
    }
  };

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
      setParentsState((prev) => {
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
        (o) => o.hierarchy.ancestors[0] === parentsState[index]
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

  const handleKey = (e, index) => {
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
  };

  const renderColumn = (column, index) => {
    return (
      <List key={index} className="tree-column">
        {column.map((option) => {
          if (
            index === 0 ||
            option.hierarchy.ancestors[0] === parentsState[index - 1]
          ) {
            return (
              <List.Item
                key={option.value}
                className={
                  option.value === parentsState[index] ||
                  option.value === value.id
                    ? "open spaced"
                    : "spaced"
                }
              >
                <List.Content
                  onClick={(e) =>
                    multiple || !isSelectable(option)
                      ? openHierarchyNode(option.value, index)()
                      : handleSelect(option, e)
                  }
                  onDoubleClick={(e) => {
                    handleSelect(option, e);
                  }}
                  onKeyDown={(e) => {
                    handleKey(e, index);
                  }}
                  tabIndex={0}
                >
                  {multiple && (
                    <Checkbox
                      checked={
                        selectedState.findIndex(
                          (item) => item.value === option.value
                        ) !== -1
                      }
                      disabled={!isSelectable(option)}
                      indeterminate={selectedState.some((item) =>
                        item.hierarchy.ancestors.includes(option.value)
                      )}
                      onChange={(e) => {
                        handleSelect(option, e);
                      }}
                    />
                  )}
                  {option.hierarchy.title[0]}
                </List.Content>

                {option.element_type === "parent" && (
                  <Button
                    className="transparent"
                    onClick={openHierarchyNode(option.value, index)}
                  >
                    {index !== columnsCount - 1 && (
                      <Icon name="angle right" color="black" />
                    )}
                  </Button>
                )}
              </List.Item>
            );
          }
        })}
      </List>
    );
  };

  return (
    <Modal
      onClose={() => setOpenState(false)}
      onOpen={() => setOpenState(true)}
      open={openState}
      className="tree-field"
    >
      <ModalHeader>
        <Grid.Row>
          <Header as="h3">{placeholder || "Choose Items"}</Header>
          <Grid.Column>
            <Input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search..."
            />
          </Grid.Column>
        </Grid.Row>
      </ModalHeader>
      <ModalContent>
        <Grid>
          <div className="columns-container">
            <Grid columns={1}>
              <Container>
                {columns.map((column, level) => (
                  <React.Fragment key={column[0]?.value}>
                    {renderColumn(column, level)}
                  </React.Fragment>
                ))}
              </Container>
            </Grid>
          </div>
        </Grid>
      </ModalContent>
      {multiple && (
        <ModalActions>
          <Grid.Row className="gapped">
            <Grid.Row className="gapped">
              {selectedState.map((i) => (
                <Label key={i.hierarchy.title}>
                  {" "}
                  <Breadcrumb icon="left angle" sections={i.hierarchy.title} />
                  <Button
                    className="small transparent"
                    onClick={(e) => {
                      handleSelect(i, e);
                    }}
                  >
                    <Icon name="delete" />
                  </Button>
                </Label>
              ))}
            </Grid.Row>
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
  root: PropTypes.string,
  openState: PropTypes.bool.isRequired,
  setOpenState: PropTypes.func.isRequired,
  allOptions: PropTypes.array.isRequired,
  value: PropTypes.oneOfType([PropTypes.array, PropTypes.object]).isRequired,
  handleSubmit: PropTypes.func.isRequired,
  selectedState: PropTypes.array.isRequired,
  setSelectedState: PropTypes.func.isRequired,
};
