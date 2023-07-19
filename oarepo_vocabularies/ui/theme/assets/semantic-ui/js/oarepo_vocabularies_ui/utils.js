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

// check if two same languages are selected in multi language field
export const checkDuplicateLanguage = (array) => {
  const languageSet = new Set();
  for (let item of array) {
    const { language } = item;
    languageSet.add(language);
  }
  return languageSet.size === array.length;
};

// turn array into shape suitable for breadcrums options
export const breadcrumbSerialization = (array) =>
  array.map((item) => ({ key: item, content: item }));
