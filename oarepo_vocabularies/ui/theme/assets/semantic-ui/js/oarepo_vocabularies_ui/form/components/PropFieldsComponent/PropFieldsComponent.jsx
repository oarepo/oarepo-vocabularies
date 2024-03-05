import React from "react";
import { Popup, Icon } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import PropTypes from "prop-types";
import { TextField, FieldLabel } from "react-invenio-forms";

export const PropFieldsComponent = ({ vocabularyProps }) => {
  const { props } = vocabularyProps;

  return (
    <React.Fragment>
      {Object.entries(props).map(([propField, propConfig]) => (
        <TextField
          required={false}
          key={propField}
          fieldPath={`props.${propField}`}
          label={
            propConfig.description ? (
              <FieldLabel
                htmlFor={propField}
                icon="pencil"
                label={
                  <React.Fragment>
                    {i18next.t(propField)}{" "}
                    <Popup
                      content={propConfig.description}
                      trigger={<Icon name="question circle" color="blue" />}
                    />
                  </React.Fragment>
                }
              />
            ) : (
              <FieldLabel
                htmlFor={propField}
                icon="pencil"
                label={i18next.t(propField)}
              />
            )
          }
        />
      ))}
    </React.Fragment>
  );
};

PropFieldsComponent.propTypes = {
  vocabularyProps: PropTypes.object.isRequired,
};
