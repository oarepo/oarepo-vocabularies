import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Item } from "semantic-ui-react";
import Overridable from "react-overridable";
import { AppContext } from "react-searchkit";
import { VocabularyItemPropsTable } from "./VocabularyResultsListItem";
import { VocabularyItemIdentifiers } from "./VocabularyItemIdentifiers";

export const FundersResultsListItem = ({ result }) => {
  const { buildUID } = useContext(AppContext);
  const { id, name, identifiers, country, props: itemProps } = result;
  return (
    <Overridable id={buildUID(`FundersResultsListItem.layout`)} result={result}>
      <Item key={id}>
        <Item.Content>
          <Item.Header as="h3">
            <a href={`/vocabularies/names/${id}`}>{name}</a> ({country})
          </Item.Header>
          <Item.Meta>
            <VocabularyItemIdentifiers identifiers={identifiers} />
          </Item.Meta>
          <Item.Description>
            {itemProps && (
              <Item.Description>
                <VocabularyItemPropsTable {...itemProps} />
              </Item.Description>
            )}
          </Item.Description>
        </Item.Content>
      </Item>
    </Overridable>
  );
};

FundersResultsListItem.propTypes = {
  result: PropTypes.shape({
    id: PropTypes.string,
    name: PropTypes.string,
    country: PropTypes.string,
    identifiers: PropTypes.arrayOf(
      PropTypes.shape({
        identifier: PropTypes.string,
        scheme: PropTypes.string,
      })
    ),
    links: PropTypes.shape({
      self: PropTypes.string,
    }),
    props: PropTypes.object,
  }),
};
