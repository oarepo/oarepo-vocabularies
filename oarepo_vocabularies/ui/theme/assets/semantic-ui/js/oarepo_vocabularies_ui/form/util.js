import * as React from "react";
import { Breadcrumb, Popup, Icon } from "semantic-ui-react";
import _join from "lodash/join";

export const serializeVocabularySuggestions = (suggestions) =>
  suggestions.map((item) => {
    if (typeof item === "string") {
      return {
        text: item,
        value: item,
        key: item,
        name: item,
        id: item,
      };
    }

    const hierarchy = item?.hierarchy?.ancestors_or_self;
    const hierarchyTitles = item?.hierarchy?.titles || [];
    let sections;
    let key = item.id;
    if (hierarchy?.length > 1) {
      key = _join(hierarchy, ".");
      sections = hierarchy.map((id, index) => ({
        key: id,
        content:
          index === 0 ? (
            hierarchyTitles[index]
          ) : (
            <span className="ui breadcrumb vocabulary-parent-item">
              {hierarchyTitles[index]}
            </span>
          ),
      }));
    }

    return {
      ...item,
      text:
        hierarchy?.length > 1 ? (
          <Breadcrumb key={key} icon="left angle" sections={sections} />
        ) : (
          item?.title_l10n || item.id
        ),
      value: item.id,
      key,
      id: item.id,
      name: item?.title_l10n || item.id,
      description: item?.description_l10n && (
        <Popup
          position="top center"
          content={item.description_l10n}
          trigger={<Icon className="ml-5" name="circle info" />}
        />
      ),
    };
  });

export const processVocabularyItems = (
  options,
  showLeafsOnly,
  filterFunction
) => {
  let serializedOptions = serializeVocabularySuggestions(options);
  if (showLeafsOnly) {
    serializedOptions = serializedOptions.filter((o) => o?.hierarchy?.leaf);
  }
  if (filterFunction) {
    serializedOptions = filterFunction(serializedOptions);
  }
  return serializedOptions;
};
