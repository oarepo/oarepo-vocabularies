import React from "react";
import PropTypes from "prop-types";
import { Label, Button, Icon } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { useFieldValue } from "../VocabularyRemoteSelectField/context";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui";

export const SelectedVocabularyValue = ({ value }) => {
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

SelectedVocabularyValue.propTypes = {
  value: PropTypes.object.isRequired,
};

export const SelectedVocabularyValues = () => {
  const { value } = useFieldValue();
  return value.map((val) => (
    <SelectedVocabularyValue key={val.id} value={val} />
  ));
};

export default SelectedVocabularyValues;

SelectedVocabularyValues.propTypes = {};

SelectedVocabularyValues.defaultProps = {};
