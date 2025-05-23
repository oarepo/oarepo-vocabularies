import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Item } from "semantic-ui-react";
import Overridable from "react-overridable";
import { AppContext } from "react-searchkit";
import { VocabularyItemIdentifiers } from "./VocabularyItemIdentifiers";
import { VocabularyItemAffiliations } from "./VocabularyItemAffiliations";

export const NamesResultsListItem = ({ result }) => {
  const { buildUID } = useContext(AppContext);
  const {
    id,
    name,
    identifiers,
    affiliations,
    links: { self_html },
  } = result;
  return (
    <Overridable id={buildUID(`NamesResultsListItem.layout`)} result={result}>
      <Item key={id}>
        <Item.Content>
          <Item.Header as="h3">
            <a href={self_html}>{name}</a>
          </Item.Header>
          <Item.Meta>
            <VocabularyItemIdentifiers identifiers={identifiers} />
            <VocabularyItemAffiliations affiliations={affiliations} />
          </Item.Meta>
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
      self_html: PropTypes.string,
    }),
  }).isRequired,
};
