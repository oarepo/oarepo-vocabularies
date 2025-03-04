// function that transforms the shape of fields with multiple values to shape accepted by api

export const transformArrayToObject = (arr) => {
  const result = {};

  arr.forEach((obj) => {
    const { language, title } = obj;
    result[language] = title;
  });

  return result;
};
