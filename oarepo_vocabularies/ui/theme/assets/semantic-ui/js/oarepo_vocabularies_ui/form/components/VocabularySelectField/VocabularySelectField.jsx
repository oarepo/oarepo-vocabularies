import React from "react";
import { Breadcrumb } from "semantic-ui-react";
import { I18nString, RelatedSelectField } from "@js/oarepo_ui";
import PropTypes from "prop-types";

export const serializeVocabularySuggestions = (suggestions) =>
  suggestions.map((item) => {
    const hierarchy = item?.hierarchy?.ancestors_or_self;
    let sections;
    if (item.hierarchy) {
      sections = [
        ...hierarchy.map((id, index, { length }) => ({
          key: id,
          content:
            index === 0 ? (
              <I18nString value={item.hierarchy.title[index]} />
            ) : (
              <span style={{ opacity: "0.5", fontSize: "0.8rem" }}>
                <I18nString value={item.hierarchy.title[index]} />
              </span>
            ),
        })),
      ];
    }
    return {
      text: item.hierarchy ? (
        <Breadcrumb icon="left angle" sections={sections} />
      ) : (
        <I18nString value={item.title} />
      ),
      value: item.id,
      key: item.id,
      data: item,
      id: item.id,
    };
  });

export const serializeVocabularyItem = (item, includeProps = ["id"]) => {
  if (typeof item === "string") {
    return { id: item };
  } else if (Array.isArray(item)) {
    return item.map((i) => serializeVocabularyItem(i));
  } else {
    return item;
  }
};

export const deserializeVocabularyItem = (item) => {
  return Array.isArray(item)
    ? item.map((item) => deserializeVocabularyItem(item))
    : item;
};

export const VocabularySelectField = ({
  type,
  fieldPath,
  externalSuggestionApi,
  multiple,
  ...restProps
}) => {
  return (
    <RelatedSelectField
      fieldPath={fieldPath}
      suggestionAPIUrl={`/api/vocabularies/${type}`}
      externalSuggestionApi={externalSuggestionApi}
      selectOnBlur={false}
      serializeSuggestions={serializeVocabularySuggestions}
      multiple={multiple}
      serializeSelectedItem={serializeVocabularyItem}
      deserializeValue={deserializeVocabularyItem}
      {...restProps}
    />
  );
};

VocabularySelectField.propTypes = {
  type: PropTypes.string.isRequired,
  fieldPath: PropTypes.string.isRequired,
  externalSuggestionApi: PropTypes.string,
  multiple: PropTypes.bool,
};

VocabularySelectField.defaultProps = {
  multiple: false,
  suggestionAPIHeaders: {
    // TODO: remove after #BE-96 gets resolved
    Accept: "application/json",
  },
};
