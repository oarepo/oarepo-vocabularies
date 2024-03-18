import React from "react";
import { Breadcrumb } from "semantic-ui-react";
import {
  I18nString,
  RelatedSelectField,
  getTitleFromMultilingualObject,
} from "@js/oarepo_ui";
import _join from "lodash/join";
import PropTypes from "prop-types";
import { search } from "../../../utils";

export const serializeVocabularySuggestions = (suggestions) =>
  suggestions.map((item) => {
    const hierarchy = item?.hierarchy?.ancestors_or_self;
    let sections;
    let key = item.id;
    if (hierarchy?.length > 1) {
      key = _join(hierarchy, ".");
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
          hierarchy.length > 1 ? (
            <Breadcrumb key={key} icon="left angle" sections={sections} />
          ) : (
            <I18nString value={item.title} />
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
      deburr
      serializeAddedValue={serializeAddedValue}
      search={search}
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
