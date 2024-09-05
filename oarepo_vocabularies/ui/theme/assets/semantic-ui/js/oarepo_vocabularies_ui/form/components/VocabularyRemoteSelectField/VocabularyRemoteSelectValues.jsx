import React from "react";

import { Label, Button, Icon, Grid } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const VocabularyRemoteSelectValue = ({ value, removeItem }) => {
  const { id, title } = value;
  return (
    <Label className="vocabulary-select-value mb-5">
      <Label.Detail className="pr-0">
        {title && typeof title === "string" ? title : id}
        <Button
          className="transparent p-0 m-0 rel-pl-1"
          onClick={() => removeItem(value)}
          type="button"
          aria-label={i18next.t("Remove")}
        >
          <Icon name="close" size="small" />
        </Button>
      </Label.Detail>
    </Label>
  );
};

export const VocabularyRemoteSelectValues = ({ fieldValue, removeItem }) => {
  return fieldValue.map((value) => (
    <VocabularyRemoteSelectValue
      key={value.id}
      value={value}
      removeItem={removeItem}
    />
  ));
};

export default VocabularyRemoteSelectValues;

VocabularyRemoteSelectValues.propTypes = {};

VocabularyRemoteSelectValues.defaultProps = {};
