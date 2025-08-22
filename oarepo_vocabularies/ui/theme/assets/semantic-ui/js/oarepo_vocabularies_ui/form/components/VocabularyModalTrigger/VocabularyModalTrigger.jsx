import * as React from "react";
import { Icon, Form } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import PropTypes from "prop-types";

export const VocabularyModalTrigger = React.forwardRef((props, ref) => {
  const { icon = "add", label, ...rest } = props;

  return (
    <Form.Button
      ref={ref}
      className="array-field-add-button inline"
      type="button"
      icon
      labelPosition="left"
      {...rest}
    >
      <Icon name={icon} />
      {label}
    </Form.Button>
  );
});

VocabularyModalTrigger.displayName = "VocabularyModalTrigger";

VocabularyModalTrigger.propTypes = {
  icon: PropTypes.string,
  label: PropTypes.string,
};

VocabularyModalTrigger.defaultProps = {
  icon: "add",
  label: i18next.t("Choose item"),
};
export default VocabularyModalTrigger;
