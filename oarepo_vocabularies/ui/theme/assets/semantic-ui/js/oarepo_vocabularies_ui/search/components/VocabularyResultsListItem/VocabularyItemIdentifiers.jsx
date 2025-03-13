import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const VocabularyItemIdentifiers = ({ identifiers }) => {
  if (!identifiers || identifiers.length === 0) {
    return null;
  }

  const itemIdentifiers = identifiers.map(({ scheme, identifier }) => {
    if (identifier.startsWith("http")) {
      return (
        <a
          href={identifier}
          target="_blank"
          rel="noopener noreferrer"
          key={identifier}
          title={scheme}
        >
          {identifier}
        </a>
      );
    } else {
      return <span title={identifier}>{identifier}</span>;
    }
  });

  return (
    <div>
      {i18next.t("Identifiers:")}{" "}
      {itemIdentifiers.map((identifier, index) => (
        <span key={identifier}>
          {identifier}
          {index < itemIdentifiers.length - 1 ? ", " : ""}
        </span>
      ))}
    </div>
  );
};

VocabularyItemIdentifiers.propTypes = {
  identifiers: PropTypes.arrayOf(
    PropTypes.shape({
      identifier: PropTypes.string.isRequired,
      scheme: PropTypes.string.isRequired,
    })
  ),
};
