import React, { useContext } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import _toPairs from "lodash/toPairs";
import _reverse from "lodash/reverse";
import { Item, Breadcrumb, Label } from "semantic-ui-react";
import { withState, AppContext } from "react-searchkit";
import { I18nString } from "@js/oarepo_ui/forms";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components";
import { getLocalizedValue } from "@js/oarepo_ui/util";
import { VocabularyItemIdentifiers } from "./VocabularyItemIdentifiers";
import { VocabularyItemAffiliations } from "./VocabularyItemAffiliations";

export const VocabularyItemPropsTable = (props) => {
  const { vocabularyProps: vocabularyPropsMetadata } = useContext(
    SearchConfigurationContext
  );
  const items = _toPairs(props).filter(([, value]) => value);
  return (
    <dl className="vocabulary-props-list">
      {items.map(([key, value]) => (
        <div className="vocabulary-props-item" key={key}>
          <dt>
            <b>{getLocalizedValue(vocabularyPropsMetadata, key)}</b>
          </dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
};

export const VocabularyResultsListItemComponent = ({ result, appName }) => {
  const { buildUID } = useContext(AppContext);
  const { vocabularyType } = useContext(SearchConfigurationContext);

  const {
    title = "No title",
    id,
    props: itemProps,
    hierarchy,
    links,
    funder,
    identifiers,
    affiliations,
  } = result;
  const ancestorTitlesWithId = hierarchy?.title?.map(
    (ancestorTitle, index) => ({
      ...ancestorTitle,
      id: hierarchy?.ancestors_or_self[index],
    })
  );
  const { self_html: selfHTML, vocabulary_html: vocabularyHTML } = links;

  return (
    <Overridable
      id={buildUID(`ResultsListItem.layout`)}
      result={result}
      title={title}
    >
      <Item key={id} className="ui vocabulary-results-list-item">
        <Item.Content>
          <Item.Header as="h2">
            <a href={selfHTML}>
              <I18nString value={title} />
            </a>
          </Item.Header>
          {hierarchy?.ancestors?.length > 0 && (
            <div>
              <Breadcrumb>
                {_reverse(ancestorTitlesWithId)?.map(
                  (ancestorTitleWithId, index) => (
                    <React.Fragment key={ancestorTitleWithId.id}>
                      <Breadcrumb.Section
                        href={`${vocabularyHTML}/${ancestorTitleWithId.id}`}
                      >
                        <I18nString value={ancestorTitleWithId} />
                      </Breadcrumb.Section>
                      {index !== ancestorTitlesWithId.length - 1 && (
                        <Breadcrumb.Divider />
                      )}
                    </React.Fragment>
                  )
                )}
              </Breadcrumb>
            </div>
          )}
          {itemProps && (
            <Item.Description>
              <VocabularyItemPropsTable {...itemProps} />
            </Item.Description>
          )}
        </Item.Content>
        <Item.Meta>
          {funder?.id && <Label>{funder?.name || funder.id}</Label>}
          <VocabularyItemIdentifiers identifiers={identifiers} />
          <VocabularyItemAffiliations affiliations={affiliations} />
        </Item.Meta>
        <Overridable
          id={buildUID(`ResultsListItem.extra.${vocabularyType}`)}
          result={result}
        />
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
  const { buildUID } = useContext(AppContext);
  const { vocabularyType } = useContext(SearchConfigurationContext);

  return (
    // not possible to use dynamic results list item, because not all vocabularies have "type" property so using URL instead
    <Overridable id={buildUID(`ResultsList.item.${vocabularyType}`)} {...props}>
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
