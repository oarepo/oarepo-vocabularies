import React from "react";
import { Label, Icon } from "semantic-ui-react";
import { MultilingualString, RelatedSelectField } from "@js/oarepo_ui";
import _reverse from "lodash/reverse";
import PropTypes from 'prop-types'

export const serializeVocabularySuggestions = (suggestions) =>
  suggestions.map((item) => ({
    text:
      item.hierarchy.ancestors.length === 0 ? (
        <MultilingualString value={item.title} />
      ) : (
        <span>
          <Label>
            {_reverse(item.hierarchy.ancestors).map((ancestor) => (
              <React.Fragment key={ancestor}>
                {ancestor}{" "}
                <Icon size="small" name="arrow right" className="ml-3" />
              </React.Fragment>
            ))}
          </Label>
          <Label color="green" className="ml-3">
            <MultilingualString value={item.title} />
          </Label>
        </span>
      ),
    value: item.id,
    key: item.id,
  }));

export const VocabularySelect = ({
  type,
  fieldPath,
  externalSuggestionApi,
  multiple,
  ...restProps
}) => {
  return (
    <RelatedSelectField
      fieldPath={fieldPath}
      suggestionAPIUrl={`/api/vocabularies/${type}`}
      externalSuggestionApi={externalSuggestionApi}
      selectOnBlur={false}
      serializeSuggestions={serializeVocabularySuggestions}
      multiple={multiple}
      {...restProps}
    />
  );
};

VocabularySelect.propTypes = {
  type: PropTypes.string.isRequired,
  fieldPath: PropTypes.string.isRequired,
  externalSuggestionApi: PropTypes.string,
  multiple: PropTypes.bool,
};

VocabularySelect.defaultProps = {
  multiple: false,
};
