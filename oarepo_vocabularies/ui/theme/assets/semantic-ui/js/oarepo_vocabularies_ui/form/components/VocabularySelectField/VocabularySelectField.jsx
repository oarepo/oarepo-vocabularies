import React from "react";
import { Breadcrumb } from "semantic-ui-react";
import { I18nString, RelatedSelectField } from "@js/oarepo_ui";
import _join from "lodash/join";
import PropTypes from "prop-types";

export const serializeVocabularySuggestions = (suggestions) =>
  suggestions.map((item) => {
    const hierarchy = item.hierarchy.ancestors_or_self;
    const key = _join(hierarchy, ".");
    const sections = [
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
        active: index === 0 && length !== 1,
      })),
    ];
    return {
      text: <Breadcrumb key={key} icon="left angle" sections={sections} />,
      value: item,
      key: key,
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
