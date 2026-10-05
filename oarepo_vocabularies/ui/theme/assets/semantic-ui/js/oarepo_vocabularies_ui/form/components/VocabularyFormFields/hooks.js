// SPDX-FileCopyrightText: 2025-2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

import { useEffect } from "react";
import { useFormikContext, getIn } from "formik";

export const useSetIdBasedOnIdentifier = (isUpdateForm) => {
  const { values, setFieldValue } = useFormikContext();

  const { scheme, identifier } = getIn(values, "identifiers.0", "");
  useEffect(() => {
    if (isUpdateForm) {
      return;
    }
    if (scheme && identifier) {
      setFieldValue("id", `${scheme}:${identifier}`);
    }
  }, [scheme, identifier, setFieldValue, isUpdateForm]);
};
