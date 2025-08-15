import React, { useContext } from "react";
import PropTypes from "prop-types";
import { Item, Label } from "semantic-ui-react";
import Overridable from "react-overridable";
import { AppContext } from "react-searchkit";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui/util";

export const AwardsResultsListItem = ({ result }) => {
  const { buildUID } = useContext(AppContext);
  const {
    id,
    number,
    title,
    funder,
    links: { self_html: selfHTML },
  } = result;
  return (
    <Overridable id={buildUID(`AwardsResultsListItem.layout`)} result={result}>
      <Item key={id}>
        <Item.Content>
          <Item.Header as="h3">
            <a href={selfHTML}>{`${getTitleFromMultilingualObject(
              title
            )} (${number})`}</a>
          </Item.Header>
          <Item.Meta>
            {funder?.id && <Label>{funder?.name || funder.id}</Label>}
          </Item.Meta>
        </Item.Content>
      </Item>
    </Overridable>
  );
};

AwardsResultsListItem.propTypes = {
  result: PropTypes.shape({
    id: PropTypes.string.isRequired,
    number: PropTypes.string.isRequired,
    title: PropTypes.object,
    funder: PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
    }),
    links: PropTypes.shape({
      self: PropTypes.string,
      self_html: PropTypes.string,
    }),
    props: PropTypes.object,
  }).isRequired,
};
