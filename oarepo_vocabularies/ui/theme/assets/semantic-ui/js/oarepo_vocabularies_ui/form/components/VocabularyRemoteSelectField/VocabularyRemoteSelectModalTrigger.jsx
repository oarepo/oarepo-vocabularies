import * as React from "react";
import { Icon, Button, Form } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import PropTypes from "prop-types";

export const VocabularyRemoteSelectModalTrigger = React.forwardRef(
  ({ label }, ref) => (
    <Button
      ref={ref}
      className="array-field-add-button"
      type="button"
      icon
      labelPosition="left"
    >
      <Icon name="add" />
      {label}
    </Button>
  )
);

VocabularyRemoteSelectModalTrigger.propTypes = {
  label: PropTypes.string,
};

VocabularyRemoteSelectModalTrigger.defaultProps = {
  label: i18next.t("Choose item"),
};
export default VocabularyRemoteSelectModalTrigger;
