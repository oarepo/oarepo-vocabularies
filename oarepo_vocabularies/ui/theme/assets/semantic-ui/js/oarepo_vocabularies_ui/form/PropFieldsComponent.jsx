import React from "react";
import { TextField } from "react-invenio-forms";

export const PropFieldsComponent = ({ vocabularyProps }) => {
  return Object.keys(vocabularyProps).map((item) => (
    <TextField
      key={item}
      fieldPath={`props.${item}`}
      label={vocabularyProps[item].label}
      width={9}
    />
  ));
};
