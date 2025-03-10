// function that transforms the shape of fields with multiple values to shape accepted by api

export const transformArrayToObject = (arr) => {
  const result = {};

  arr.forEach((obj) => {
    const { language, title } = obj;
    result[language] = title;
  });

  return result;
};

export const extractVocabularyTypeFromCurrentURL = () => {
  try {
    const currentURL = window.location.href;

    const parsedURL = new URL(currentURL);
    const pathSegments = parsedURL.pathname.split("/");

    if (pathSegments.length > 2) {
      return pathSegments[2];
    } else {
      return null; // Or throw an error
    }
  } catch (error) {
    console.error("Error extracting vocabulary name:", error);
    return null; // Or throw the error
  }
};
