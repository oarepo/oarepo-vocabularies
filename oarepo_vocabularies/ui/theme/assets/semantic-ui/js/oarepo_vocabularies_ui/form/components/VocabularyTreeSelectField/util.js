import _has from "lodash/has";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { processVocabularyItems } from "../../util";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui/util";

export const isSelectable = (option) => {
  return _has(option, "selectable") ? !!option.selectable : true;
};

export const isDescendant = (option, ancestorId) => {
  return option.hierarchy.ancestors.includes(ancestorId);
};

export const isColumnOptionHidden = (option, columnIndex, columns) => {
  return (
    !isSelectable(option) &&
    (option.element_type === "leaf" ||
      (option.element_type === "parent" &&
        (columnIndex < columns.length - 1
          ? !columns[columnIndex + 1][1].some((child) =>
              isDescendant(child, option.value)
            )
          : true)))
  );
};

export const sortByTitle = (options) =>
  options.sort((a, b) => {
    const titleComparison = a.hierarchy.ancestors?.[0]?.localeCompare(
      b.hierarchy.ancestors[0],
      i18next.language,
      { sensitivity: "base" }
    );
    if (titleComparison !== 0) {
      return titleComparison;
    } else {
      return getTitleFromMultilingualObject(a.hierarchy.title[0]).localeCompare(
        getTitleFromMultilingualObject(b.hierarchy.title[0]),
        i18next.language,
        { sensitivity: "base" }
      );
    }
  });

export const vocabularyItemsToColumnOptions = (
  items,
  root,
  showLeafsOnly,
  filterFunction
) => {
  return processVocabularyItems(
    root ? items.filter((option) => isDescendant(option, root)) : items,
    showLeafsOnly,
    filterFunction
  );
};

export const isParent = (option, options) => {
  return options.some(
    (opt) =>
      opt.hierarchy.ancestors.includes(option.value) && option.id !== opt.id
  );
};

export const suggestionsToColumnOptions = (
  items,
  root,
  showLeafsOnly,
  filterFunction
) => {
  const serializedOptions = vocabularyItemsToColumnOptions(
    items,
    root,
    showLeafsOnly,
    filterFunction
  );

  return serializedOptions.map((val) => ({
    ...val,
    element_type: isParent(val, serializedOptions) ? "parent" : "leaf",
  }));
};
