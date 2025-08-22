import * as React from "react";
import PropTypes from "prop-types";
import { List, Icon, Label, Header } from "semantic-ui-react";
import { getTitleFromMultilingualObject } from "@js/oarepo_ui/util";

export const InternalResultListItem = ({
  result,
  handleSelect = () => {},
  selected,
}) => {
  const { title, relatedURI } = result;

  return (
    <List.Item
      onClick={() => handleSelect(result, selected)}
      className={`search-result-item ${selected ? "selected" : ""}`}
      active={selected}
    >
      <List.Content>
        <Header className="mb-5" size="small">
          {getTitleFromMultilingualObject(title)}{" "}
          {relatedURI &&
            Object.entries(relatedURI).map(([name, value]) => (
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
  selected: PropTypes.bool,
};

InternalResultListItem.defaultProps = {
  handleSelect: () => {},
  selected: false,
};
