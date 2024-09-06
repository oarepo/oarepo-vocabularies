import React from "react";
import PropTypes from "prop-types";
import { Label, Button, Icon } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { useFieldValue } from "./context";

export const VocabularyRemoteSelectValue = ({ value }) => {
  const { value: fieldValue, removeValue } = useFieldValue();
  const { id, title } = value ?? fieldValue;
  return (
    <Label className="vocabulary-select-value mb-5">
      <Label.Detail className="pr-0">
        {title && typeof title === "string" ? title : id}
        <Button
          className="transparent p-0 m-0 rel-pl-1"
          onClick={() => removeValue(value)}
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
