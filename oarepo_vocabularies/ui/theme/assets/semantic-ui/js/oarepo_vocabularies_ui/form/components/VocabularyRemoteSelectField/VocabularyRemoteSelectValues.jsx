import React from "react";
import PropTypes from "prop-types";
import { Label, Button, Icon } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { useFieldValue } from "./context";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui";

export const VocabularyRemoteSelectValue = ({ value }) => {
  const { value: fieldValue, removeValue } = useFieldValue();
  const _value = value ?? fieldValue;
  const { title, id } = _value;

  const itemTitle =
    getTitleFromMultilingualObject(title) ??
    (id ?? typeof _value === "string" ? _value : i18next.t("Unknown item"));

  return (
    <Label className="vocabulary-select-value mb-5">
      <Label.Detail className="pr-0">
        {itemTitle}
        <Button
          className="transparent p-0 m-0 rel-pl-1"
          onClick={() => removeValue(_value)}
          type="button"
          aria-label={i18next.t("Remove")}
        >
          <Icon name="close" size="small" />
        </Button>
      </Label.Detail>
    </Label>
  );
};

VocabularyRemoteSelectValue.propTypes = {
  value: PropTypes.object,
};

export const VocabularyRemoteSelectValues = () => {
  const { value } = useFieldValue();
  return value.map((val) => (
    <VocabularyRemoteSelectValue key={value.id} value={val} />
  ));
};

export default VocabularyRemoteSelectValues;

VocabularyRemoteSelectValues.propTypes = {};

VocabularyRemoteSelectValues.defaultProps = {};
