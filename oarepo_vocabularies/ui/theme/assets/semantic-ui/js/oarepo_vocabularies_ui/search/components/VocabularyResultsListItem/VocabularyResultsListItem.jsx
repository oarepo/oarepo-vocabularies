import React, { useContext } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import _toPairs from "lodash/toPairs";
import _chunk from "lodash/chunk";
import _reverse from "lodash/reverse";
import { Item, Table, Label, Grid, Icon } from "semantic-ui-react";
import { withState, buildUID } from "react-searchkit";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { I18nString } from "@js/oarepo_ui";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components";

const VocabularyItemPropsTable = (props) => {
  // Split properties into max. 4 tables of max. 2 rows
  const tables = _chunk(_toPairs(props), 2).slice(0, 4);

  return (
    <Grid celled="internally" columns={tables.length} className="dense">
      {tables.map((tableData, index) => (
        <Grid.Column key={index}>
          <Table basic="very" collapsing compact>
            <Table.Body>
              {tableData.map(([key, value]) => (
                <Table.Row key={key}>
                  <Table.Cell>
                    <b>{i18next.t(key)}</b>
                  </Table.Cell>
                  <Table.Cell>{value}</Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table>
        </Grid.Column>
      ))}
    </Grid>
  );
};

export const VocabularyResultsListItemComponent = ({ result, appName }) => {
  const {
    title = "No title",
    id,
    props: itemProps,
    hierarchy: { ancestors },
  } = result;
  const {
    ui_links: { search },
  } = useContext(SearchConfigurationContext);
  const viewLink = new URL(id, search);
  return (
    <Overridable
      id={buildUID("RecordsResultsListItem.layout", "", appName)}
      result={result}
      title={title}
    >
      <Item key={id}>
        <Item.Content>
          <Item.Header as="h2">
            <a href={viewLink}>
              <I18nString value={title} />
            </a>
            <Label tag pointing="left" size="small">
              <b>ID</b>
              {ancestors &&
                _reverse(ancestors).map((ancestor) => (
                  <Label.Detail
                    as="a"
                    href={`${search}/${ancestor}`}
                    key={ancestor}
                  >
                    {`${ancestor}`}
                    {"-->"}
                  </Label.Detail>
                ))}
              <Label.Detail>{id}</Label.Detail>
            </Label>
          </Item.Header>
          {itemProps && (
            <Item.Description>
              <VocabularyItemPropsTable {...itemProps} />
            </Item.Description>
          )}
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
