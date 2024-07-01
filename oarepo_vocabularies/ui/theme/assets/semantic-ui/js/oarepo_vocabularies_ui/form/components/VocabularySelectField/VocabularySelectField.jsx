import React from "react";
import { Breadcrumb } from "semantic-ui-react";
import {
  RelatedSelectField,
  getTitleFromMultilingualObject,
} from "@js/oarepo_ui";
import _join from "lodash/join";
import PropTypes from "prop-types";

export const serializeVocabularySuggestions = (suggestions) =>
  suggestions.map((item) => {
    const hierarchy = item?.hierarchy?.ancestors_or_self;
    let sections;
    let key = item.id;
    if (hierarchy?.length > 1) {
      key = _join(hierarchy, ".");
      sections = [
        ...hierarchy.map((id, index) => ({
          key: id,
          content:
            index === 0 ? (
              getTitleFromMultilingualObject(item.hierarchy.title[index])
            ) : (
              <span className="ui breadcrumb vocabulary-parent-item">
                {getTitleFromMultilingualObject(item.hierarchy.title[index])}
              </span>
            ),
        })),
      ];
    }
    if (typeof item === "string") {
      return {
        text: item,
        value: item,
        key: item,
        name: item,
        id: item,
      };
    } else {
      return {
        text:
          hierarchy?.length > 1 ? (
            <Breadcrumb key={key} icon="left angle" sections={sections} />
          ) : (
            getTitleFromMultilingualObject(item?.title) || item.id
          ),
        value: item.id,
        key: key,
        data: item,
        id: item.id,
        title: item.title,
        name: getTitleFromMultilingualObject(item?.title),
      };
    }
  });

// for adding free text items
const serializeAddedValue = (value) => {
  return { text: value, value, key: value, name: value, id: value };
};

export const VocabularySelectField = ({
  type,
  fieldPath,
  externalAuthority,
  multiple,
  ...restProps
}) => {
  const suggestionsConfig = {
    suggestionAPIUrl: `/api/vocabularies/${type}`,
  };
  if (externalAuthority) {
    suggestionsConfig.externalSuggestionApi = `${suggestionsConfig.suggestionAPIUrl}/authoritative`;
  }
  return (
    <RelatedSelectField
      fieldPath={fieldPath}
      {...suggestionsConfig}
      selectOnBlur={false}
      serializeSuggestions={serializeVocabularySuggestions}
      multiple={multiple}
      deburr
      serializeAddedValue={serializeAddedValue}
      {...restProps}
    />
  );
};

VocabularySelectField.propTypes = {
  type: PropTypes.string.isRequired,
  fieldPath: PropTypes.string.isRequired,
  externalAuthority: PropTypes.bool,
  multiple: PropTypes.bool,
};

VocabularySelectField.defaultProps = {
  multiple: false,
  externalAuthority: false,
  suggestionAPIHeaders: {
    // TODO: remove after #BE-96 gets resolved
    Accept: "application/json",
  },
};
