import * as React from "react";
import PropTypes from "prop-types";
import { List, Icon, Label, Header } from "semantic-ui-react";

export const InternalResultListItem = ({ result, handleSelect = () => {} }) => {
  const { id, title, relatedURI } = result;

  return (
    <List.Item
      onClick={() => handleSelect(result)}
      className="search-result-item"
    >
      <List.Content>
        <Header className="mb-5" size="small">
          {title}{" "}
          {Object.entries(relatedURI).map(([name, value]) => (
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
          ))}
        </Header>
      </List.Content>
    </List.Item>
  );
};

InternalResultListItem.propTypes = {
  result: PropTypes.object.isRequired,
  handleSelect: PropTypes.func,
};

InternalResultListItem.defaultProps = {
  handleSelect: () => {},
};
