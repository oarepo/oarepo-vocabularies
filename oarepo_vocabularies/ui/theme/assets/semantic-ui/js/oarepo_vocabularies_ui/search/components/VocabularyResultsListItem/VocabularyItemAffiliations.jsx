import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const VocabularyItemAffiliations = ({ affiliations }) => {
  if (!affiliations || affiliations.length === 0) {
    return null;
  }

  return (
    <div>
      {i18next.t("Affiliations:")}{" "}
      {affiliations.map((affiliation, index) => (
        <span key={affiliation.name}>
          {affiliation.name}
          {index < affiliations.length - 1 ? ", " : ""}
        </span>
      ))}
    </div>
  );
};

VocabularyItemAffiliations.propTypes = {
  affiliations: PropTypes.arrayOf(PropTypes.string).isRequired,
};
