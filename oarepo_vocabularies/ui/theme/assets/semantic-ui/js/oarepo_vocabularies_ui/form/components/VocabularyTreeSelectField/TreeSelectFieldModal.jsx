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
} from "semantic-ui-react";
import { processVocabularyItems } from "@js/oarepo_vocabularies";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const TreeSelectFieldModal = ({
  fieldPath,
  multiple,
  placeholder,
  root,
  query,
  setQuery,
  openState,
  setOpenState,
  allOptions,
  value,
  handleSubmit,
  selectedState,
  setSelectedState,
  ...uiProps
}) => {
  const serializedOptions = useMemo(
    () => processVocabularyItems(allOptions),
    [allOptions]
  );

  const [parentsState, setParentsState] = useState([]);
  const [keybState, setKeybState] = useState([]);

  const hierarchicalData = useMemo(() => {
    const map = new Map();
    let excludeFirstGroup = false;

    serializedOptions.forEach((option) => {
      const ancestorCount = option.hierarchy.ancestors.length;

      if (root && option.value == root) {
        excludeFirstGroup = true;
      }

      if (!(root && excludeFirstGroup && ancestorCount === 0)) {
        if (!map.has(ancestorCount)) {
          map.set(ancestorCount, []);
        }
        map.get(ancestorCount).push(option);
      }
    });

    map.forEach((options, _) => {
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
    });

    let result = Array.from(map.entries())
      .sort((a, b) => a[0] - b[0])
      .filter(
        ([ancestorCount, _]) =>
          !(root && excludeFirstGroup && ancestorCount === 0)
      )
      .map(([_, options]) => {
        if (root) {
          return options.filter(
            (option) =>
              option.hierarchy.ancestors.includes(root) ||
              option.hierarchy.ancestors.length === 0
          );
        } else {
          return options;
        }
      })
      .filter((group) => group.length > 0)
      .map((group) => {
        return group;
      });

    return query === ""
      ? result
      : result.map((group) =>
          group.filter((option) =>
            option.hierarchy.title[0]
              .toLowerCase()
              .includes(query.toLowerCase())
          )
        );
  }, [serializedOptions, query, root]);

  const columnsCount = hierarchicalData.length;

  const openHierarchyNode = (parent, level) => () => {
    let updatedParents = [...parentsState];
    updatedParents.splice(level + 1);
    updatedParents[level] = parent;

    let updatedKeybState = [...keybState];

    const columnOptions = hierarchicalData[level];
    const nextColumnIndex = columnOptions.findIndex((o) => o.value === parent);
    updatedKeybState.splice(level + 1);
    updatedKeybState[level] = nextColumnIndex;

    setParentsState(updatedParents);
    setKeybState(updatedKeybState);
  };
  const handleSelect = (option, e) => {
    e.preventDefault();

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
      updateSelectedState(option, existingParentIndex, childIndexes);
    } else {
      setSelectedState([option]);
    }
  };

  const updateSelectedState = (option, existingParentIndex, childIndexes) => {
    setSelectedState((prevState) =>
      updateState(prevState, option, existingParentIndex, childIndexes)
    );
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
      const nextColumnOptions = hierarchicalData[index + 1];
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
    const data = hierarchicalData[index];

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
      <Grid.Column key={index} className="tree-column">
        {column.map((option, i) => {
          if (
            index == 0 ||
            option.hierarchy.ancestors[0] == parentsState[index - 1]
          ) {
            return (
              <Grid.Row
                key={option.value}
                className={
                  option.value == parentsState[index] ? "open spaced" : "spaced"
                }
              >
                {multiple && (
                  <Checkbox
                    checked={
                      selectedState.findIndex(
                        (item) => item.value === option.value
                      ) !== -1
                    }
                    indeterminate={selectedState.some((item) =>
                      item.hierarchy.ancestors.includes(option.value)
                    )}
                    onChange={(e) => {
                      handleSelect(option, e);
                    }}
                  />
                )}
                <Button
                  basic
                  color="black"
                  onClick={openHierarchyNode(option.value, index)}
                  onDoubleClick={(e) => {
                    handleSelect(option, e);
                  }}
                  onKeyDown={(e) => {
                    handleKey(e, index);
                  }}
                  tabIndex={0}
                >
                  {option.hierarchy.title[0]}
                </Button>
                {option.element_type == "parent" && (
                  <Button onClick={openHierarchyNode(option.value, index)}>
                    {index !== columnsCount - 1 && (
                      <Icon name="angle right" color="black" />
                    )}
                  </Button>
                )}
              </Grid.Row>
            );
          }
        })}
      </Grid.Column>
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
                {hierarchicalData.map((column, level) => (
                  <React.Fragment key={column[0]?.value}>
                    {renderColumn(column, level)}
                  </React.Fragment>
                ))}
              </Container>
            </Grid>
          </div>
        </Grid>
      </ModalContent>
      <ModalActions>
        <Grid.Row className="gapped">
          <Grid.Row className="gapped">
            {selectedState.map((i, index) => (
              <Label key={i.hierarchy.title}>
                {" "}
                <Breadcrumb icon="left angle" sections={i.hierarchy.title} />
                {multiple && (
                  <Button
                    className="small transparent"
                    onClick={(e) => {
                      handleSelect(i, e);
                    }}
                  >
                    <Icon name="delete" />
                  </Button>
                )}
              </Label>
            ))}
          </Grid.Row>
          <Button
            content="Confirm"
            labelPosition="right"
            floated="right"
            icon="checkmark"
            onClick={handleSubmit}
            secondary
          />
        </Grid.Row>
      </ModalActions>
    </Modal>
  );
};

TreeSelectFieldModal.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  multiple: PropTypes.bool,
  placeholder: PropTypes.string,
  root: PropTypes.string,
  query: PropTypes.string.isRequired,
  setQuery: PropTypes.func.isRequired,
  openState: PropTypes.bool.isRequired,
  setOpenState: PropTypes.func.isRequired,
  allOptions: PropTypes.array.isRequired,
  value: PropTypes.oneOfType([PropTypes.array, PropTypes.object]).isRequired,
  handleSubmit: PropTypes.func.isRequired,
  selectedState: PropTypes.array.isRequired,
  setSelectedState: PropTypes.func.isRequired,
};
