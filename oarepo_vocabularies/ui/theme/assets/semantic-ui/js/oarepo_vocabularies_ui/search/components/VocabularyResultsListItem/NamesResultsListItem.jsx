import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Item, Label } from "semantic-ui-react";
import Overridable from "react-overridable";
import { AppContext } from "react-searchkit";
import { VocabularyItemPropsTable } from "./VocabularyResultsListItem";
import { VocabularyItemIdentifiers } from "./VocabularyItemIdentifiers";

export const NamesResultsListItem = ({ result }) => {
  const { buildUID } = useContext(AppContext);
  const { id, name, identifiers, affiliations, props: itemProps } = result;
  return (
    <Overridable id={buildUID(`NamesResultsListItem.layout`)} result={result}>
      <Item key={id}>
        <Item.Content>
          <Item.Header as="h3">
            <a href={`/vocabularies/names/${id}`}>{name}</a>
          </Item.Header>
          <Item.Meta>
            <VocabularyItemIdentifiers identifiers={identifiers} />
            {affiliations?.length > 0 && (
              <Label.Group>
                {affiliations.map(({ name }, index) => (
                  <Label key={name}>{name}</Label>
                ))}
              </Label.Group>
            )}
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

NamesResultsListItem.propTypes = {
  result: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    identifiers: PropTypes.arrayOf(
      PropTypes.shape({
        identifier: PropTypes.string.isRequired,
        scheme: PropTypes.string.isRequired,
      })
    ),
    affiliations: PropTypes.arrayOf(
      PropTypes.shape({
        name: PropTypes.string.isRequired,
      })
    ),
    links: PropTypes.shape({
      self: PropTypes.string,
    }),
    props: PropTypes.object,
  }).isRequired,
};
