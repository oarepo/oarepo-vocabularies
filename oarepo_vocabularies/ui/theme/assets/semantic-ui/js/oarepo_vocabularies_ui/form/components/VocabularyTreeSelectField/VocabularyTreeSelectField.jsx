import React, { useMemo, useState } from "react";
import { SelectField } from "react-invenio-forms";
import { useFormConfig } from "@js/oarepo_ui";
import { useFormikContext, getIn } from "formik";
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
import { processVocabularyItems } from "../LocalVocabularySelectField";
import { useTranslation } from "react-i18next";

export const VocabularyTreeSelectField = ({
  fieldPath,
  multiple,
  optionsListName,
  helpText,
  placeholder,
  category,
  optimized,
  ...uiProps
}) => {
  const { formConfig } = useFormConfig();
  const { vocabularies } = formConfig;
  const formik = useFormikContext();
  const { values, setFieldTouched } = useFormikContext();
  const value = getIn(values, fieldPath, multiple ? [] : {});
  let { all: allOptions, featured: featuredOptions } =
    vocabularies[optionsListName];

  if (!allOptions) {
    console.error(
      `Do not have options for ${optionsListName} inside:`,
      vocabularies
    );
  }

  const serializedOptions = useMemo(
    () => processVocabularyItems(allOptions),
    [allOptions]
  );
  const { i18n } = useTranslation();

  const [openState, setOpenState] = useState(false);
  const [parentsState, setParentsState] = useState([]);
  const [keybState, setKeybState] = useState([]);

  const [selectedState, setSelectedState] = useState(() => {
    if (multiple && Array.isArray(value)) {
      return value.reduce((acc, val) => {
        const foundOption = serializedOptions.find(
          (option) => option.value === val.id
        );
        if (foundOption) {
          acc.push(foundOption);
        }
        return acc;
      }, []);
    } else {
      return [];
    }
  });

  const handleOpen = (e) => {
    if (e.currentTarget.classList.contains("icon")) return;
    setOpenState(true);
  };
  const [query, setQuery] = useState("");

  const hierarchicalData = useMemo(() => {
    let data = [];
    let currentColumn = [];
    let currentLevel = 1;
    serializedOptions.forEach((option) => {
      if (option.hierarchy.ancestors.includes(category) || !category) {
        if (option.hierarchy.ancestors.length === currentLevel) {
          currentColumn.push(option);
        } else {
          currentColumn.sort((a, b) =>
            a.hierarchy.title[0].localeCompare(
              b.hierarchy.title[0],
              i18n.language,
              { sensitivity: "base" }
            )
          );
          data.push(currentColumn);
          currentColumn = [option];
          currentLevel = option.hierarchy.ancestors.length;
        }
      }
    });

    if (currentColumn.length > 0) {
      currentColumn.sort((a, b) =>
        a.hierarchy.title[0].localeCompare(
          b.hierarchy.title[0],
          i18n.language,
          { sensitivity: "base" }
        )
      );
      data.push(currentColumn);
    }

    return query === ""
      ? data
      : data.map((column) =>
          column.filter((option) =>
            option.hierarchy.title[0]
              .toLowerCase()
              .includes(query.toLowerCase())
          )
        );
  }, [serializedOptions, category, query]);

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
    } else {
      if (multiple && selectedState.length !== 0) {
        setSelectedState((prevState) => {
          let newState = prevState;
          if (childIndexes.length > 0) {
            childIndexes.forEach((childIndex, i) => {
              newState = newState.filter(
                (_, index) => index !== childIndex - i
              );
            });
            return [...newState, option];
          } else if (existingParentIndex !== -1) {
            newState = prevState.filter(
              (_, index) => index !== existingParentIndex
            );
            return [...newState, option];
          } else {
            return [...prevState, option];
          }
        });
      } else {
        setSelectedState([option]);
      }
    }
  };

  const handleSubmit = () => {
    const prepSelect = [
      ...selectedState.map((item) => {
        return {
          id: item.value,
          title: [
            ...item.hierarchy.title.map((i) => {
              return { cs: i };
            }),
          ],
        };
      }),
    ];
    formik.setFieldValue(fieldPath, multiple ? prepSelect : prepSelect[0]);
    setOpenState(false);
    setSelectedState([]);
    setParentsState([]);
  };

  const handleChange = ({ e, data }) => {
    if (multiple) {
      let vocabularyItems = allOptions.filter((o) =>
        data.value.includes(o.value)
      );
      vocabularyItems = vocabularyItems.map((vocabularyItem) => {
        return { ...vocabularyItem, id: vocabularyItem.value };
      });
      formik.setFieldValue(fieldPath, [...vocabularyItems]);
      setSelectedState(vocabularyItems);
    } else {
      let vocabularyItem = allOptions.find((o) => o.value === data.value);
      vocabularyItem = { ...vocabularyItem, id: vocabularyItem?.value };
      formik.setFieldValue(fieldPath, vocabularyItem);
      setSelectedState(vocabularyItem);
    }
  };

  const handleKey = (e, index) => {
    e.preventDefault();
    let newIndex = 0;

    index = keybState.length - 1 > index ? keybState.length - 1 : index;
    let data = hierarchicalData[index];

    const moveKey = (index, newIndex, back = false) => {
      setKeybState((prev) => {
        const newState = [...prev];
        if (back) {
          newState.splice(index, 1);
        } else {
          newState[index] = newIndex;
        }
        return newState;
      });
    };

    if (
      e.key === "ArrowUp" ||
      (e.shiftKey && e.key === "ArrowUp") ||
      (e.ctrlKey && e.key === "ArrowUp")
    ) {
      newIndex = keybState[index] - 1;
      if (newIndex >= 0) {
        openHierarchyNode(data[newIndex].value, index)();
        moveKey(index, newIndex, false);
      }
      if (e.shiftKey && e.key === "ArrowUp") {
        handleSelect(data[newIndex], e);
      }
    } else if (
      e.key === "ArrowDown" ||
      (e.shiftKey && e.key === "ArrowDown") ||
      (e.ctrlKey && e.key === "ArrowDown") ||
      e.key === "Tab"
    ) {
      newIndex = keybState[index] + 1;

      if (newIndex < data.length) {
        openHierarchyNode(data[newIndex].value, index)();
        moveKey(index, newIndex, false);
      }
      if (e.shiftKey && e.key === "ArrowDown") {
        handleSelect(data[newIndex], e);
      }
    } else if (e.key === "ArrowLeft") {
      if (index > 0) {
        setParentsState((prev) => {
          const newState = [...prev];
          newState.splice(index, 1);
          return newState;
        });
        moveKey(index, null, true);
      }
    } else if (e.key === "ArrowRight") {
      if (index < columnsCount - 1) {
        const nextColumnOptions = hierarchicalData[index + 1];
        if (nextColumnOptions) {
          const nextColumnIndex = nextColumnOptions.findIndex(
            (o) => o.hierarchy.ancestors[0] === parentsState[index]
          );
          if (nextColumnIndex !== -1) {
            newIndex = nextColumnIndex;
            openHierarchyNode(
              nextColumnOptions[nextColumnIndex].value,
              index + 1
            )();
            moveKey(index + 1, newIndex, false);
          }
        }
      }
    } else if (
      e.key === "Enter" ||
      (e.ctrlKey && e.key === " ") ||
      e.key == " "
    ) {
      handleSelect(data[keybState[index]], e);
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
    <React.Fragment>
      <SelectField
        selectOnBlur={false}
        optimized={optimized}
        onBlur={() => setFieldTouched(fieldPath)}
        deburr
        fieldPath={fieldPath}
        multiple={multiple}
        featured={featuredOptions}
        options={serializedOptions}
        onClick={(e) => handleOpen(e)}
        onChange={handleChange}
        value={multiple ? value.map((o) => o?.id) : value?.id}
        {...uiProps}
      />
      <label className="helptext">{helpText}</label>

      {openState && (
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
                      <React.Fragment key={level}>
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
                  <Label key={index}>
                    {" "}
                    <Breadcrumb
                      icon="left angle"
                      sections={i.hierarchy.title}
                    />
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
      )}
    </React.Fragment>
  );
};

VocabularyTreeSelectField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  multiple: PropTypes.bool,
  optionsListName: PropTypes.string.isRequired,
  helpText: PropTypes.string,
  noResultsMessage: PropTypes.string,
  optimized: PropTypes.bool,
  placeholder: PropTypes.string,
  category: PropTypes.string,
};

VocabularyTreeSelectField.defaultProps = {
  noResultsMessage: "No results found.",
  optimized: false,
};
