import * as React from "react";
import { Breadcrumb, Popup, Icon } from "semantic-ui-react";
import _join from "lodash/join";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui/util";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

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
        ...item,
        text:
          hierarchy?.length > 1 ? (
            <Breadcrumb key={key} icon="left angle" sections={sections} />
          ) : (
            getTitleFromMultilingualObject(item?.title) || item.id
          ),
        value: item.id,
        key: key,
        id: item.id,
        // really funky issue with SUI where if title is a string, the dropdown crashes. And as
        // we are using vnd serialization now, you get title as a string
        title:
          typeof item?.title === "string"
            ? { [i18next.language]: item?.title }
            : item?.title,
        name: getTitleFromMultilingualObject(item?.title),
      };
    }
  });

export function serializeVocabularyItems(vocabularyItems) {
  return (
    vocabularyItems
      // BE returns empty vocabulary items (for single selection vocabulary fields)that are objects with some keys.
      //  Check if this makes sense?
      .filter((vocabularyItem) => vocabularyItem.id)
      .map((vocabularyItem) => {
        const title = getTitleFromMultilingualObject(vocabularyItem.title);
        const titlesArray = vocabularyItem?.hierarchy?.title || [];
        const sections = titlesArray.map((title, index) => {
          if (index === 0) {
            return {
              content: <span>{getTitleFromMultilingualObject(title)}</span>,
              key: crypto.randomUUID(),
            };
          } else {
            return {
              content: (
                <span className="ui breadcrumb vocabulary-parent-item">
                  {getTitleFromMultilingualObject(title)}
                </span>
              ),
              key: crypto.randomUUID(),
            };
          }
        });

        return {
          id: vocabularyItem.id || vocabularyItem.value,
          value: vocabularyItem.id || vocabularyItem.value,
          text: title,
          key: vocabularyItem.id || vocabularyItem.value,
          content:
            titlesArray.length <= 1 ? (
              <span>{title}</span>
            ) : (
              <Breadcrumb icon="left angle" sections={sections} />
            ),
          description: vocabularyItem.description && (
            <Popup
              position="top center"
              content={vocabularyItem.description}
              trigger={<Icon className="ml-5" name="circle info" />}
            />
          ),
          name: getTitleFromMultilingualObject(vocabularyItem.title),
          props: vocabularyItem.props,
          hierarchy: vocabularyItem.hierarchy,
        };
      })
  );
}

export const processVocabularyItems = (
  options,
  showLeafsOnly,
  filterFunction
) => {
  let serializedOptions = serializeVocabularyItems(options);
  if (showLeafsOnly) {
    serializedOptions = serializedOptions.filter((o) => o?.hierarchy?.leaf);
  }
  if (filterFunction) {
    serializedOptions = filterFunction(serializedOptions);
  }
  return serializedOptions;
};
