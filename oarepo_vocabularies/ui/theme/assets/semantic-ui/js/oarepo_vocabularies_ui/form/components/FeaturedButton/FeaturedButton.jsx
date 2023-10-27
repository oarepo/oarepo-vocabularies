import React from "react";
import { Button } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { useFormikContext, getIn } from "formik";

export const FeaturedButton = () => {
  const { setFieldValue, values, isSubmitting } = useFormikContext();
  const tags = getIn(values, "tags", []);
  const isFeatured = tags.includes("featured");
  return (
    <Button
      fluid
      toggle
      active={isFeatured}
      disabled={isSubmitting}
      loading={isSubmitting}
      color="blue"
      icon="star"
      labelPosition="left"
      content={i18next.t("Feature")}
      title={i18next.t('Item will be displayed on top of form input options')}
      type="button"
      onClick={() =>
        setFieldValue(
          "tags",
          isFeatured
            ? tags.filter((t) => t !== "featured")
            : [...tags, "featured"]
        )
      }
    />
  );
};
