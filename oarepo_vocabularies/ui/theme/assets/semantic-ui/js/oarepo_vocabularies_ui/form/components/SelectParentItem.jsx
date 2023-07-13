import React, { useEffect, useState } from "react";
// import { RemoteSelectField } from "react-invenio-forms";
import { getIn, useFormikContext } from "formik";
import { RemoteSelectField } from "./RemoteSelectField";
import { http } from "react-invenio-forms";
// for testing purposes

const serializeSuggestions = (suggestions) =>
  suggestions.map((item) => ({
    text: item.title?.cs,
    value: item.id,
    key: item.id,
  }));

export const SelectParentItem = ({ vocabularyRecord }) => {
  const { values } = useFormikContext();
  console.log(vocabularyRecord);
  const [initialParent, setInitialParent] = useState({});
  let getParentInfoApiUrl;
  if (vocabularyRecord.hierarchy.parent) {
    getParentInfoApiUrl = `/api/vocabularies/institutions/${vocabularyRecord.hierarchy.parent}`;
  }
  const fieldPath = "h-parent";
  useEffect(() => {
    if (!vocabularyRecord.hierarchy.parent) return;
    http
      .get(getParentInfoApiUrl)
      .then((response) => setInitialParent(response.data.data));
  }, [vocabularyRecord]);
  return (
    <RemoteSelectField
      clearable
      onValueChange={({ formikProps }, selectedSuggestions) => {
        formikProps.form.setFieldValue(
          fieldPath,
          // save the suggestion objects so we can extract information
          // about which value added by the user
          selectedSuggestions[0]
        );
      }}
      fieldPath={fieldPath}
      initialSuggestions={[initialParent]}
      serializeSuggestions={serializeSuggestions}
      suggestionAPIUrl="/api/vocabularies/institutions"
      // suggestionAPIHeaders={{
      //   Accept: "application/vnd.inveniordm.v1+json",
      // }}
      suggestionAPIHeaders={{
        Accept: "application/json",
      }}
      value={
        getIn(values, fieldPath, {}).value
          ? getIn(values, fieldPath, {}).value
          : ""
      }
      // value={
      //   getIn(values, fieldPath, [])[0]?.value
      //     ? getIn(values, fieldPath, [])[0].value
      //     : ""
      // }
      width={11}
    />
  );
};
