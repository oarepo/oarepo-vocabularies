import React, { useContext } from "react";
import { Button } from "semantic-ui-react";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const NewItemButton = () => {
  const { ui_links: uiLinks, permissions } = useContext(
    SearchConfigurationContext
  );

  return permissions?.can_create ? (
    <React.Fragment>
      <Button
        as="a"
        href={uiLinks.create}
        fluid
        color="green"
        icon="plus"
        labelPosition="left"
        content={i18next.t("newItem")}
        type="button"
        className="computer only"
      />
      <Button
        as="a"
        href={uiLinks.create}
        fluid
        color="green"
        icon="plus"
        labelPosition="left"
        content={i18next.t("newItem")}
        type="button"
        className="mobile tablet only rel-mt-2"
      />
    </React.Fragment>
  ) : null;
};
