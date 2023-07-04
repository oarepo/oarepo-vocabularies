import React from "react";
import { TextField } from "react-invenio-forms";
import { Label } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import PropTypes from "prop-types";

export const PropFieldsComponent = ({ vocabularyProps }) => {
  console.log(vocabularyProps);
  const { props } = vocabularyProps;
  return Object.keys(props).map((item) => {
    return (
      <React.Fragment key={item}>
        <TextField
          fieldPath={`props.${item}`}
          label={i18next.t(item)}
          width={11}
        />
        {props[item].description && (
          <Label pointing="above">{props[item].description}</Label>
        )}
      </React.Fragment>
    );
  });
};

PropFieldsComponent.propTypes = {
  vocabularyProps: PropTypes.object.isRequired,
};
