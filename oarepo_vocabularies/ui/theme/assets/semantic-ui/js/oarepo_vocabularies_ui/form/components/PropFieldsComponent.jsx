import React from "react";
import { TextField } from "react-invenio-forms";
import { Popup, Icon } from "semantic-ui-react";
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
          label={
            props[item].description ? (
              <Popup
                content={props[item].description}
                trigger={
                  <label>
                    {i18next.t(item)}
                    <Icon name="question circle" color="blue" />
                  </label>
                }
              />
            ) : (
              i18next.t(item)
            )
          }
          width={11}
        />
      </React.Fragment>
    );
  });
};

PropFieldsComponent.propTypes = {
  vocabularyProps: PropTypes.object.isRequired,
};
