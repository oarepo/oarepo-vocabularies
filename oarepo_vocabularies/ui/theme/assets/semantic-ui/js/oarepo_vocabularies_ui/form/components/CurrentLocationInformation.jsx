// component to show the user where they currently are

import React from "react";
import { useAxios } from "../hooks/useAxios";
import { Message, Breadcrumb } from "semantic-ui-react";
import _ from "lodash";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { breadcrumbSerialization } from "../../utils";
import { ErrorComponent } from "./Error";
import PropTypes from "prop-types";
import { useFormConfig } from "@js/oarepo_ui/forms";

const NewTopLevelItemMessage = () => (
  <Message
    icon="attention"
    header={i18next.t("newItemMessage")}
    size="tiny"
    // don't understand how to reasonably set width for such a component in semantic!!
    style={{ width: "68%" }}
  />
);

const NewChildItemMessage = ({ newChildItemParentId }) => {
  const { response, loading, error } = useAxios({
    url: `/api/vocabularies/institutions/${newChildItemParentId}`,
  });
  return (
    <React.Fragment>
      {!loading && !error.message && (
        <Message
          icon="attention"
          header={i18next.t("newChildItemMessage", {
            item: response?.title?.cs,
          })}
          size="tiny"
          content={
            <Breadcrumb
              icon="right angle"
              sections={[
                ..._.reverse(
                  breadcrumbSerialization(
                    response?.hierarchy?.ancestors_or_self
                  )
                ),
                { key: "new", content: i18next.t("newItem"), active: true },
              ]}
            />
          }
          // don't understand how to reasonably set width for such a component in semantic!!
          style={{ width: "68%" }}
        />
      )}
      {error.message && <ErrorComponent error={error} />}
    </React.Fragment>
  );
};

const EditMessage = ({ record }) => {
  const {
    hierarchy: { level, ancestors_or_self },
  } = record;
  if (level === 1)
    return (
      <Message
        icon="attention"
        header={i18next.t("editTopLevelItemMessage")}
        size="tiny"
        // don't understand how to reasonably set width for such a component in semantic!!
        style={{ width: "68%" }}
      />
    );
  return (
    <Message
      icon="attention"
      header={i18next.t("editChildItemMessage")}
      size="tiny"
      content={
        <Breadcrumb
          icon="right angle"
          sections={_.reverse(breadcrumbSerialization(ancestors_or_self))}
        />
      }
      // don't understand how to reasonably set width for such a component in semantic!!
      style={{ width: "68%" }}
    />
  );
};

export const CurrentLocationInformation = ({
  newChildItemParentId,
  editMode,
}) => {
  const { record } = useFormConfig();
  if (!editMode && !newChildItemParentId) {
    return <NewTopLevelItemMessage />;
  } else if (!editMode) {
    return <NewChildItemMessage newChildItemParentId={newChildItemParentId} />;
  } else {
    return <EditMessage record={record} />;
  }
};

NewChildItemMessage.propTypes = {
  newChildItemParentId: PropTypes.string.isRequired,
};

EditMessage.propTypes = {
  record: PropTypes.shape({
    hierarchy: PropTypes.shape({
      level: PropTypes.number.isRequired,
      ancestors_or_self: PropTypes.arrayOf(PropTypes.string),
    }).isRequired,
  }).isRequired,
};

CurrentLocationInformation.propTypes = {
  newChildItemParentId: PropTypes.string,
  editMode: PropTypes.bool,
  record: PropTypes.shape({
    hierarchy: PropTypes.shape({
      level: PropTypes.number.isRequired,
      ancestors_or_self: PropTypes.arrayOf(PropTypes.string),
    }),
  }),
};
