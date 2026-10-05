// SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

// function that transforms the shape of fields with multiple values to shape accepted by api

export const transformArrayToObject = (arr) => {
  const result = {};

  arr.forEach((obj) => {
    const { language, title } = obj;
    result[language] = title;
  });

  return result;
};
