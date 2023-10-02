import React, { useContext } from "react";
import { Button } from "semantic-ui-react";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const ClearFiltersButton = () => {
  const { ui_links } = useContext(SearchConfigurationContext);
  return (
    <Button
      className="rel-mt-2"
      as="a"
      href={ui_links.search}
      fluid
      color="yellow"
      icon="cancel"
      labelPosition="left"
      content={i18next.t("Clear filters")}
      type="button"
    />
  );
};
