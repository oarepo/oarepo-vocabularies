import { useEffect } from "react";
import { useFormikContext, getIn } from "formik";

export const useSetIdBasedOnIdentifier = (editMode) => {
  const { values, setFieldValue } = useFormikContext();

  const { scheme, identifier } = getIn(values, "identifiers.0", "");
  useEffect(() => {
    if (editMode) {
      return;
    }
    if (scheme && identifier) {
      setFieldValue("id", `${scheme}:${identifier}`);
    }
  }, [scheme, identifier, setFieldValue, editMode]);
};
