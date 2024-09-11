import * as React from "react";
import { Icon, Form } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import PropTypes from "prop-types";

export const VocabularyRemoteSelectModalTrigger = React.forwardRef(
  (props, ref) => {
    const { label, ...rest } = props;

    return (
      <Form.Button
        ref={ref}
        className="array-field-add-button"
        type="button"
        icon
        labelPosition="left"
        {...rest}
      >
        <Icon name="add" />
        {label}
      </Form.Button>
    );
  }
);

VocabularyRemoteSelectModalTrigger.propTypes = {
  label: PropTypes.string,
};

VocabularyRemoteSelectModalTrigger.defaultProps = {
  label: i18next.t("Choose item"),
};
export default VocabularyRemoteSelectModalTrigger;
