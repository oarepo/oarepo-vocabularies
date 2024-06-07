// function that transforms the shape of fields with multiple values to shape accepted by api
import _deburr from "lodash/deburr";
import _escapeRegExp from "lodash/escapeRegExp";
import _filter from "lodash/filter";

export const transformArrayToObject = (arr) => {
  const result = {};

  arr.forEach((obj) => {
    const { language, title } = obj;
    result[language] = title;
  });

  return result;
};

// custom search function to avoid the issue of not being able to search
// through text in react nodes that are our dropdown options
// requires also name to be returned in serializer which is actually a text
// value
export const search = (filteredOptions, searchQuery) => {
  const strippedQuery = _deburr(searchQuery);

  const re = new RegExp(_escapeRegExp(strippedQuery), "i");

  filteredOptions = _filter(filteredOptions, (opt) =>
    re.test(_deburr(opt?.name))
  );
  return filteredOptions;
};
