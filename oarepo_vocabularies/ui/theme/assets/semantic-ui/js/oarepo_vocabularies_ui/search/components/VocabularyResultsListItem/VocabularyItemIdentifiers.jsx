import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { ClipboardCopyButton } from "@js/oarepo_ui/components/ClipboardCopyButton";

export const VocabularyItemIdentifiers = ({ identifiers = [] }) => {
  if (!identifiers || identifiers.length === 0) {
    return null;
  }

  const itemIdentifiers = identifiers.map(({ scheme, identifier }) => ({
    scheme,
    identifier,
    isLink: identifier.startsWith("http"),
  }));

  return (
    <div>
      {i18next.t("Identifiers:")}{" "}
      {itemIdentifiers.map((item, index) => (
        <span key={item.identifier}>
          {item.isLink ? (
            <a
              href={item.identifier}
              target="_blank"
              rel="noopener noreferrer"
              title={item.scheme}
            >
              {item.identifier}
            </a>
          ) : (
            <span title={item.scheme}>{item.identifier}</span>
          )}
          <ClipboardCopyButton copyText={item.identifier} />
          {index < itemIdentifiers.length - 1 ? ", " : ""}
        </span>
      ))}
    </div>
  );
};

/* eslint-disable react/require-default-props */
VocabularyItemIdentifiers.propTypes = {
  identifiers: PropTypes.arrayOf(
    PropTypes.shape({
      identifier: PropTypes.string.isRequired,
      scheme: PropTypes.string.isRequired,
    })
  ),
};
/* eslint-enable react/require-default-props */
