import * as React from "react";
import PropTypes from "prop-types";
import { List, Icon, Label, Header } from "semantic-ui-react";
import _join from "lodash/join";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui/util";

export const ExternalResultListItem = ({
  result,
  handleSelect = () => {},
  selected,
}) => {
  // This is just a very basic knowledge-less component to display
  // pretty much anything coming from an external vocabulary API source.
  //
  // Feel free to override it to fit your use-case using overridable id:
  // VocabularyRemoteSelect.ext.ResultsList.item
  //
  const { relatedURI, title, props } = result;

  const uriLinks =
    relatedURI &&
    Object.entries(relatedURI).map(([name, value]) => {
      return (
        <Label key={name} basic size="mini">
          <a
            onClick={(e) => e.stopPropagation()}
            href={value}
            target="_blank"
            rel="noopener noreferrer"
          >
            <Icon name="external alternate" />
            {name}
          </a>
        </Label>
      );
    });

  const propValues = _join(Object.values(props), ", ");

  const onSelect = (result) => {
    handleSelect(result, selected);
  };

  return (
    <List.Item
      onClick={() => onSelect(result)}
      className="search-external-result-item"
      active={selected}
    >
      <List.Content>
        <Header className="mb-5" size="small">
          {getTitleFromMultilingualObject(title)} {uriLinks}
        </Header>
        <List.Description>{propValues}</List.Description>
      </List.Content>
    </List.Item>
  );
};

ExternalResultListItem.propTypes = {
  result: PropTypes.object.isRequired,
  handleSelect: PropTypes.func,
  selected: PropTypes.bool,
};

ExternalResultListItem.defaultProps = {
  handleSelect: () => {},
  selected: false,
};
