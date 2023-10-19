import React from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import {useFormikContext, getIn} from 'formik'

export const FeaturedButton = () => {
  const { setFieldValue, values, isSubmitting } = useFormikContext();
  const isFeatured = getIn(values, "tags", []).includes("featured");
  return (
    <Button
      fluid
      disabled={isSubmitting}
      loading={isSubmitting}
      color="blue"
      icon="star"
      labelPosition="left"
      content={i18next.t("Toggle featured")}
      type="button"
    />
  );
};
