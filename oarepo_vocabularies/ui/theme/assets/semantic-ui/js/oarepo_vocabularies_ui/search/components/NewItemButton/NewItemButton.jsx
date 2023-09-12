import React, { useContext } from "react";
import { Button } from "semantic-ui-react";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const NewItemButton = () => {
  const { ui_links } = useContext(SearchConfigurationContext);
  return (
    <Button
      as="a"
      href={ui_links.create}
      fluid
      color="green"
      icon="plus"
      labelPosition="left"
      content={i18next.t("newItem")}
      type="button"
    />
  );
};
