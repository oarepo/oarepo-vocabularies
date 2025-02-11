// component to show the user where they currently are

import React from "react";
import _reverse from "lodash/reverse";
import _isEmpty from "lodash/isEmpty";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import {
  ErrorElement,
  useFormConfig,
  OARepoDepositApiClient,
  OARepoDepositSerializer,
} from "@js/oarepo_ui";
import PropTypes from "prop-types";
import { VocabularyBreadcrumbMessage } from "./VocabularyBreadcrumbMessage";
import { VocabularyBreadcrumb } from "./VocabularyBreadcrumb";
import { useQuery } from "@tanstack/react-query";
import { Dimmer, Loader } from "semantic-ui-react";

const breadcrumbSerialization = (array) =>
  array.map((item) => ({ key: item, content: item }));

const NewTopLevelItemMessage = () => (
  <VocabularyBreadcrumbMessage header={i18next.t("newItemMessage")} />
);
const NewChildItemMessage = ({ record, newChildItemParentId }) => {
  const {
    record: { type },
    formConfig: { createUrl },
  } = useFormConfig();

  // We just need to read the parent vocabulary to get the title
  const recordSerializer = new OARepoDepositSerializer(["errors", "expanded"], ["__key"]);
  const apiClient = new OARepoDepositApiClient(createUrl, recordSerializer);

  async function read(recordUrl) {
    return await apiClient.readDraft({ self: recordUrl });
  }

  const { data, isLoading, error } = useQuery({
    queryKey: ["item", newChildItemParentId],
    queryFn: () => read(`/api/vocabularies/${type}/${newChildItemParentId}`),
  });

  if (isLoading)
    return (
      <Dimmer active inverted>
        <Loader inverted>Loading</Loader>
      </Dimmer>
    );

  const localizedVocabularyTitle = !_isEmpty(data) ? 
    data.title[i18next.language] || data.title[i18next.options.fallbackLng] || Object.values(data.title).shift() : "";

  return (
    <React.Fragment>
      {!isLoading && data && (
        <VocabularyBreadcrumbMessage
          header={
            `${i18next.t("newChildItemMessage")} ${localizedVocabularyTitle}`
          }
          content={
            <VocabularyBreadcrumb
              sections={[
                ..._reverse(
                  breadcrumbSerialization(data.hierarchy?.ancestors_or_self)
                ),
                {
                  key: "new",
                  content: !_isEmpty(record?.id) ? record.id : i18next.t("newItem"),
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
  editMode,
}) => {
  const { record } = useFormConfig();
  if (!editMode && !newChildItemParentId) {
    return <NewTopLevelItemMessage />;
  } else if (!editMode) {
    return <NewChildItemMessage record={record} newChildItemParentId={newChildItemParentId} />;
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
