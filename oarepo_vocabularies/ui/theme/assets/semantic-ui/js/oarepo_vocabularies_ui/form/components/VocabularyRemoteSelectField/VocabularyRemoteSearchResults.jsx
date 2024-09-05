import React from "react";
import Overridable from "react-overridable";
import { withState } from "react-searchkit";
import { List, Header, Label, Icon, Button } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const VocabularyRemoteSearchResults = withState(
  ({
    currentResultsState: results,
    currentQueryState: { size: querySize },
    handleSelect,
    findMore,
    source,
    values,
  }) => {
    const notEnoughResults = querySize > results.data.hits.length;

    return (
      <List verticalAlign="middle" selection size="small">
        {results.data.hits.map((result) => {
          const { id, title, relatedURI } = result;
          console.log({ result });
          return (
            <Overridable
              key={id}
              id={`VocabularyRemoteSelect.${source}.ResultsList.item`}
              result={result}
            >
              <List.Item
                onClick={() => handleSelect(result)}
                className="search-result-item"
                //   active={true}
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
            </Overridable>
          );
        })}
        {notEnoughResults && (
          <List.Item
            className="search-result-item"
            key="_find-more"
            onClick={() => findMore()}
          >
            <Header color="blue" className="mb-5" size="small">
              {i18next.t("Find more records …")}
            </Header>
          </List.Item>
        )}
      </List>
    );
  }
);

VocabularyRemoteSearchResults.propTypes = {};

VocabularyRemoteSearchResults.defaultProps = {};

export default VocabularyRemoteSearchResults;
