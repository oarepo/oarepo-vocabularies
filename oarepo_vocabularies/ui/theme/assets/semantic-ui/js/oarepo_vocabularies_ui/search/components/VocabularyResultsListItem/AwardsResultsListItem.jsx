import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Item, Label } from "semantic-ui-react";
import Overridable from "react-overridable";
import { AppContext } from "react-searchkit";
import { VocabularyItemPropsTable } from "./VocabularyResultsListItem";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui";

export const AwardsResultsListItem = ({ result }) => {
  const { buildUID } = useContext(AppContext);
  const { id, number, title, funder, props: itemProps } = result;
  return (
    <Overridable id={buildUID(`AwardsResultsListItem.layout`)} result={result}>
      <Item key={id}>
        <Item.Content>
          <Item.Header as="h3">
            <a
              href={`/vocabularies/awards/${id}`}
            >{`${getTitleFromMultilingualObject(title)} (${number})`}</a>
          </Item.Header>
          <Item.Meta>
            {funder?.id && <Label>{funder?.name || funder.id}</Label>}
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

AwardsResultsListItem.propTypes = {
  result: PropTypes.shape({
    id: PropTypes.string.isRequired,
    number: PropTypes.string.isRequired,
    title: PropTypes.object.isRequired,
    funder: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string,
        name: PropTypes.string,
      })
    ),
    props: PropTypes.object,
  }).isRequired,
};
