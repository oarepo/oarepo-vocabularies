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

// turn array into shape suitable for breadcrums options
export const breadcrumbSerialization = (array) =>
  array.map((item) => ({ key: item, content: item }));
