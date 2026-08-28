import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { ClipboardCopyButton } from "@js/oarepo_ui/components/ClipboardCopyButton";

export const VocabularyItemCrosswalks = ({ crosswalks = [] }) => {
  if (!crosswalks || crosswalks.length === 0) {
    return null;
  }

  const itemCrosswalks = crosswalks.map(({ scheme, identifier }) => ({
    scheme,
    identifier,
    isLink: identifier.startsWith("http"),
  }));

  return (
    <div>
      {i18next.t("Crosswalks from external systems:")}{" "}
      {itemCrosswalks.map((item, index) => (
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
          {index < itemCrosswalks.length - 1 ? ", " : ""}
        </span>
      ))}
    </div>
  );
};

/* eslint-disable react/require-default-props */
VocabularyItemCrosswalks.propTypes = {
  crosswalks: PropTypes.arrayOf(
    PropTypes.shape({
      identifier: PropTypes.string.isRequired,
      scheme: PropTypes.string.isRequired,
    })
  ),
};
/* eslint-enable react/require-default-props */
