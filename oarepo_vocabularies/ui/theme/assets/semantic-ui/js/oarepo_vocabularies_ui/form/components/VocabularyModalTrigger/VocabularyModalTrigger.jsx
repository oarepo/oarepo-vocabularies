import * as React from "react";
import { Icon, Form } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import PropTypes from "prop-types";

export const VocabularyModalTrigger = React.forwardRef((props, ref) => {
  const { label, ...rest } = props;

  return (
    <Form.Button
      ref={ref}
      className="array-field-add-button inline"
      type="button"
      icon
      labelPosition="left"
      {...rest}
    >
      <Icon name="add" />
      {label}
    </Form.Button>
  );
});

VocabularyModalTrigger.propTypes = {
  label: PropTypes.string,
};

VocabularyModalTrigger.defaultProps = {
  label: i18next.t("Choose item"),
};
export default VocabularyModalTrigger;
