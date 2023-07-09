// TODO: this utility could be moved to oarepo-ui
export const getInputFromDOM = (elementName) => {
  const element = document.getElementsByName(elementName);
  if (element.length > 0 && element[0].hasAttribute("value")) {
    return JSON.parse(element[0].value);
  }
  return null;
};

// functiona that temporarily resolves getting vocabulary type from url
export const extractVariablePart = (url) => {
  const regex = /\/vocabularies\/([^/]+)/;
  const match = url.match(regex)?.[1];
  return match || null; // or any default value you prefer
};

// function that transforms the shape of fields with multiple values to shape accepted by api

export const transformArrayToObject = (arr) => {
  const result = {};

  arr.forEach((obj) => {
    const { language, title } = obj;
    result[language] = title;
  });

  return result;
};

// function that creates array suitable for formik arrayfield
export const translateObjectToArray = (obj) => {
  const result = [];

  Object.keys(obj).forEach((language) => {
    const title = obj[language];
    result.push({ language, title });
  });

  return result;
};

//   function to clear all values in an object

export const clearObjectValues = (obj) => {
  const result = {};

  for (let key in obj) {
    result[key] = "";
  }

  return result;
};

// check if two same languages are selected in multi language field
export const checkDuplicateLanguage = (array) => {
  const languageSet = new Set();
  for (let item of array) {
    const { language } = item;
    languageSet.add(language);
  }
  return languageSet.size === array.length;
};

export const scrollTop = () => {
  window.scrollTo({
    top: 0,
    left: 0,
    behavior: "smooth",
  });
};
