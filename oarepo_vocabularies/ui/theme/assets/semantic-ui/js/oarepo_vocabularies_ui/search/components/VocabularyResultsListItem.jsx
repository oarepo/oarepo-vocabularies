import React, { useContext } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";

import _get from "lodash/get";
import _join from "lodash/join";
import _truncate from "lodash/truncate";
import _upperFirst from "lodash/upperFirst";

import { Item, Label, Icon } from "semantic-ui-react";
import { withState, buildUID } from "react-searchkit";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components";

import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const VocabularyResultsListItemComponent = ({
  currentQueryState,
  result,
  appName,
}) => {
  const searchAppConfig = useContext(SearchConfigurationContext);

  console.log(result);
  const title = _upperFirst(_get(result, "title_l10n", "No title"));

  const viewLink = new URL(
    "",
    new URL(searchAppConfig.ui_endpoint, window.location.origin)
  );
  return (
    <Overridable
      id={buildUID("RecordsResultsListItem.layout", "", appName)}
      result={result}
      title={title}
    >
      <Item key={result.id}>
        <Item.Content>
          <Item.Extra className="labels-actions"></Item.Extra>
          <Item.Header as="h2">
            <a href={viewLink}>{title}</a>
          </Item.Header>
          <Item.Description></Item.Description>
        </Item.Content>
      </Item>
    </Overridable>
  );
};

VocabularyResultsListItemComponent.propTypes = {
  currentQueryState: PropTypes.object,
  result: PropTypes.object.isRequired,
  appName: PropTypes.string,
};

VocabularyResultsListItemComponent.defaultProps = {
  currentQueryState: null,
  appName: "",
};

export const VocabularyResultsListItem = (props) => {
  return (
    <Overridable
      id={buildUID("VocabularyResultsListItem", "", props.appName)}
      {...props}
    >
      <VocabularyResultsListItemComponent {...props} />
    </Overridable>
  );
};

VocabularyResultsListItem.propTypes = {
  currentQueryState: PropTypes.object,
  result: PropTypes.object.isRequired,
  appName: PropTypes.string,
};

VocabularyResultsListItem.defaultProps = {
  currentQueryState: null,
  appName: "",
};

export const VocabularyResultsListItemWithState = withState(
  ({ currentQueryState, result, appName }) => (
    <VocabularyResultsListItem
      currentQueryState={currentQueryState}
      result={result}
      appName={appName}
    />
  )
);

VocabularyResultsListItemWithState.propTypes = {
  currentQueryState: PropTypes.object,
  result: PropTypes.object.isRequired,
};

VocabularyResultsListItemComponent.defaultProps = {
  currentQueryState: null,
};
