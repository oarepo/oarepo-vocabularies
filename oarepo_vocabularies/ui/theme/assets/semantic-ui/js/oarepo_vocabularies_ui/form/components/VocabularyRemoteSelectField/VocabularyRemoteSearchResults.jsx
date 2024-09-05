import React from "react";
import PropTypes from "prop-types";
import { withState } from "react-searchkit";
import { List, Header, Label, Icon } from "semantic-ui-react";

export const VocabularyRemoteSearchResults = withState(
  ({ currentResultsState: results, handleSelect, values }) => {
    return (
      <List verticalAlign="middle" selection size="small">
        {results.data.hits.map((result) => {
          const { id, title, relatedURI, description } = result;
          return (
            <List.Item
              key={id}
              onClick={() => {
                handleSelect(result);
              }}
              className="search-result-item"
              //   active={true}
            >
              <List.Content>
                <Header className="mb-5" size="small">
                  {title}{" "}
                  {Object.entries(relatedURI).map(([name, value]) => (
                    <Label basic size="mini">
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
        })}
      </List>
    );
  }
);

VocabularyRemoteSearchResults.propTypes = {};

VocabularyRemoteSearchResults.defaultProps = {};

export default VocabularyRemoteSearchResults;
