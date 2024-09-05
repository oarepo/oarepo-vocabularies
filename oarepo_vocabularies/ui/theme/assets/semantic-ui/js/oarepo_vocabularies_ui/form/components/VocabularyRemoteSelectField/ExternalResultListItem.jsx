import * as React from "react";
import PropTypes from "prop-types";
import { List, Icon, Label, Header } from "semantic-ui-react";
import _join from "lodash/join";

export const ExternalResultListItem = ({ result, handleSelect = () => {} }) => {
  // This is just a very basic knowledge-less component to display
  // pretty much anything coming from an external vocabulary API source.
  //
  // Feel free to override it to fit your use-case using overridable id:
  // VocabularyRemoteSelect.ext.ResultsList.item
  //
  const { id, relatedURI, props } = result;

  const uriLinks = Object.entries(relatedURI).map(([name, value]) => {
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
    // TODO: here you can convert the result to internal format
    handleSelect(result);
  };

  return (
    <List.Item
      onClick={() => onSelect(result)}
      className="search-external-result-item"
      //   active={true}
    >
      <List.Content>
        <Header className="mb-5" size="small">
          {id} {uriLinks}
        </Header>
        <List.Description>{propValues}</List.Description>
      </List.Content>
    </List.Item>
  );
};

ExternalResultListItem.propTypes = {
  result: PropTypes.object.isRequired,
  handleSelect: PropTypes.func,
};

ExternalResultListItem.defaultProps = {
  handleSelect: () => {},
};
