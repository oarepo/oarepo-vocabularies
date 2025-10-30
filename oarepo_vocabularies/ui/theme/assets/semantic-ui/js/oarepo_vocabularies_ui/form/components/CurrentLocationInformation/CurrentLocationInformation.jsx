// component to show the user where they currently are

import React from "react";
import _reverse from "lodash/reverse";
import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { useFormConfig } from "@js/oarepo_ui/forms";
import { ErrorElement } from "@js/oarepo_ui/search";
import { getLocalizedValue, httpApplicationJson } from "@js/oarepo_ui/util";
import PropTypes from "prop-types";
import { VocabularyBreadcrumbMessage } from "./VocabularyBreadcrumbMessage";
import { VocabularyBreadcrumb } from "./VocabularyBreadcrumb";
import { useQuery } from "@tanstack/react-query";
import { Dimmer, Loader } from "semantic-ui-react";

const breadcrumbSerialization = (array) =>
  array.map((item) => ({ key: item, content: item }));

async function read(recordUrl) {
  const res = await httpApplicationJson.get(recordUrl);
  return res.data;
}

const NewTopLevelItemMessage = () => (
  <VocabularyBreadcrumbMessage header={i18next.t("newItemMessage")} />
);
const NewChildItemMessage = ({ record, newChildItemParentId }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ["item", newChildItemParentId],
    queryFn: () => read(record.links?.parent),
  });

  if (isLoading)
    return (
      <Dimmer active inverted>
        <Loader inverted>{i18next("Loading")}</Loader>
      </Dimmer>
    );

  const localizedVocabularyTitle = _isEmpty(data)
    ? ""
    : getLocalizedValue(data.title);

  return (
    <React.Fragment>
      {!isLoading && data && (
        <VocabularyBreadcrumbMessage
          header={`${i18next.t(
            "newChildItemMessage"
          )} ${localizedVocabularyTitle}`}
          content={
            <VocabularyBreadcrumb
              sections={[
                ..._reverse(
                  breadcrumbSerialization(data.hierarchy?.ancestors_or_self)
                ),
                {
                  key: "new",
                  content: _isEmpty(record?.id)
                    ? i18next.t("newItem")
                    : record.id,
                  active: true,
                },
              ]}
            />
          }
        />
      )}
      {error?.message && <ErrorElement error={error} />}
    </React.Fragment>
  );
};

NewChildItemMessage.propTypes = {
  record: PropTypes.object.isRequired,
  newChildItemParentId: PropTypes.string,
};

const EditMessage = ({ record }) => {
  const {
    hierarchy: { level, ancestors_or_self },
  } = record;
  if (level === 1)
    return (
      <VocabularyBreadcrumbMessage
        header={i18next.t("editTopLevelItemMessage")}
      />
    );
  return (
    <VocabularyBreadcrumbMessage
      header={i18next.t("editChildItemMessage")}
      content={
        <VocabularyBreadcrumb
          sections={_reverse(breadcrumbSerialization(ancestors_or_self))}
        />
      }
    />
  );
};

export const CurrentLocationInformation = ({
  newChildItemParentId,
  isUpdateForm,
}) => {
  const { record } = useFormConfig();
  if (!record?.hierarchy?.level) return null;

  if (!isUpdateForm) {
    if (!newChildItemParentId) {
      return <NewTopLevelItemMessage />;
    }
    return (
      <NewChildItemMessage
        record={record}
        newChildItemParentId={newChildItemParentId}
      />
    );
  }
  return <EditMessage record={record} />;
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

/* eslint-disable react/require-default-props */
CurrentLocationInformation.propTypes = {
  newChildItemParentId: PropTypes.string,
  isUpdateForm: PropTypes.bool.isRequired,
};
/* eslint-enable react/require-default-props */
