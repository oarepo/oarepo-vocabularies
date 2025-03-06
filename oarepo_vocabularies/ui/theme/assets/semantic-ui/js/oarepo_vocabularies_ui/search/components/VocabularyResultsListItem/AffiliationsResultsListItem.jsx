import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Item } from "semantic-ui-react";
import Overridable from "react-overridable";
import { AppContext } from "react-searchkit";
import { VocabularyItemPropsTable } from "./VocabularyResultsListItem";
import { VocabularyItemIdentifiers } from "./VocabularyItemIdentifiers";

export const AffiliationsResultsListItem = ({ result }) => {
  const { buildUID } = useContext(AppContext);
  const { id, name, identifiers, props: itemProps } = result;
  return (
    <Overridable
      id={buildUID(`AffiliationsResultsListItem.layout`)}
      result={result}
    >
      <Item key={id}>
        <Item.Content>
          <Item.Header as="h3">
            <a href={`/vocabularies/affiliations/${id}`}>{name}</a>
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

AffiliationsResultsListItem.propTypes = {
  result: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    identifiers: PropTypes.arrayOf(
      PropTypes.shape({
        identifier: PropTypes.string.isRequired,
        scheme: PropTypes.string.isRequired,
      })
    ),
    links: PropTypes.shape({
      self: PropTypes.string,
    }),
    props: PropTypes.object,
  }).isRequired,
};
