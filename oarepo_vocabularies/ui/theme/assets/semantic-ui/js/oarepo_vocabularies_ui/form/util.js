import * as React from 'react'
import { Breadcrumb } from "semantic-ui-react";
import _join from "lodash/join";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui";

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
        title: item.title,
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
    return {
      ...vocabularyItem,
      text:
        titlesArray.length === 1 ? (
          <span>{text}</span>
        ) : (
          <Breadcrumb icon="left angle" sections={sections} />
        ),
      name: text,
      icon: undefined,
    };
  });
