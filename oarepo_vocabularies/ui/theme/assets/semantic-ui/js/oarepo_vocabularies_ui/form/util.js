import * as React from "react";
import { Breadcrumb, Popup, Icon } from "semantic-ui-react";
import _join from "lodash/join";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui";
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

export const serializeVocabularyItems = (vocabularyItems) =>
  vocabularyItems.map((vocabularyItem) => {
    const {
      hierarchy: { title: titlesArray },
      text,
    } = vocabularyItem;
    const sections = [
      ...titlesArray.map((title, index) => {
        if (index === 0) {
          return {
            content: <span>{title}</span>,
            key: crypto.randomUUID(),
          };
        } else {
          return {
            content: (
              <span className="ui breadcrumb vocabulary-parent-item">
                {title}
              </span>
            ),
            key: crypto.randomUUID(),
          };
        }
      }),
    ];
    // the dropdown uses "description" prop to show the description, but it
    // does not look very nice, so we remove it from the vocabulary item and use it how it suits us
    const { description, ...vocabularyItemWithoutDescription } = vocabularyItem;
    return {
      ...vocabularyItemWithoutDescription,
      text:
        titlesArray.length === 1 ? (
          <React.Fragment>
            <span>{text}</span>
            {description && (
              <Popup
                content={description}
                trigger={<Icon name="circle info" />}
              />
            )}
          </React.Fragment>
        ) : (
          <React.Fragment>
            <Breadcrumb icon="left angle" sections={sections} />
            {description && (
              <Popup
                position="top center"
                content={description}
                trigger={<Icon className="ml-5" name="circle info" />}
              />
            )}
          </React.Fragment>
        ),
      name:
        "title" in vocabularyItem
          ? getTitleFromMultilingualObject(vocabularyItem.title)
          : text,
      icon: undefined,
    };
  });
