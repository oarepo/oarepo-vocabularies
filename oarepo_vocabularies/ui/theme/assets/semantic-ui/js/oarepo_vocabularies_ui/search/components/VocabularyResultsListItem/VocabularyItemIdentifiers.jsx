import React from "react";
import { Label } from "semantic-ui-react";
import PropTypes from "prop-types";

export const VocabularyItemIdentifiers = ({ identifiers }) => {
  return identifiers?.length > 0 ? (
    <Label.Group>
      {identifiers.map(({ scheme, identifier }) => (
        <Label title={scheme} key={identifier}>
          {identifier}
        </Label>
      ))}
    </Label.Group>
  ) : null;
};

VocabularyItemIdentifiers.propTypes = {
  identifiers: PropTypes.arrayOf(
    PropTypes.shape({
      identifier: PropTypes.string.isRequired,
      scheme: PropTypes.string.isRequired,
    })
  ),
};
