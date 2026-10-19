// SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

import React from "react";
import { Popup, Icon } from "semantic-ui-react";
import PropTypes from "prop-types";
import { TextField, FieldLabel } from "react-invenio-forms";
import { useFormikContext } from "formik";
import _mapValues from "lodash/mapValues";

export const PropFieldsComponent = ({ vocabularyProps }) => {
  const { initialValues } = useFormikContext();
  // props stored on the item stay editable even when the vocabulary type does not configure them
  const props = {
    ..._mapValues(initialValues.props, () => ({})),
    ...vocabularyProps.props,
  };
  return (
    <React.Fragment>
      {Object.entries(props).map(([propField, propConfig]) => (
        <TextField
          required={false}
          key={propField}
          // bracket path keeps keys like "schema.org" from being split into nested fields
          fieldPath={`props['${propField}']`}
          label={
            propConfig.description ? (
              <FieldLabel
                htmlFor={propField}
                icon="pencil"
                label={
                  <React.Fragment>
                    {propConfig?.label || propField}{" "}
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
                label={propConfig?.label || propField}
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
