import * as React from "react";
import PropTypes from "prop-types";
import {
  ReactSearchKit,
  InvenioSearchApi,
  InvenioSuggestionApi,
} from "react-searchkit";
import { OverridableContext } from "react-overridable";
import { SearchSource } from "./constants";
import Qs from "qs";
import { serializeVocabularySuggestions } from "../../util";

class SuggestionRequestSerializer {
  constructor() {
    this.serialize = this.serialize.bind(this);
  }

  /**
   * Return a serialized version of the app state `query` for the API backend.
   * @param {object} stateQuery the `query` state to serialize
   */
  serialize(stateQuery) {
    const { suggestionString } = stateQuery;

    const getParams = {};
    if (suggestionString !== null) {
      getParams["suggest"] = suggestionString;
      getParams["size"] = 10;
    }

    return Qs.stringify(getParams, { arrayFormat: "repeat", encode: false });
  }
}

class SuggestionResponseSerializer {
  constructor() {
    this.serialize = this.serialize.bind(this);
  }

  _serializeSuggestions = (responseHits) => {
    return Array.from(new Set(serializeVocabularySuggestions(responseHits)));
  };

  /**
   * Return a serialized version of the API backend response for the app state `suggestions`.
   * @param {object} payload the backend response payload
   */
  serialize(payload) {
    return {
      suggestions: this._serializeSuggestions(payload.hits.hits || []),
    };
  }
}

export const MultiSourceSearchApp = React.memo(
  ({
    source,
    vocabulary,
    overriddenComponents,
    queryState,
    children,
    ...rest
  }) => {
    const sources = {
      [SearchSource.INTERNAL]: {
        searchApi: {
          axios: {
            headers: {
              Accept: "application/json",
            },
            url: `/api/vocabularies/${vocabulary}`,
          },
        },
      },
      [SearchSource.EXTERNAL]: {
        searchApi: {
          axios: {
            headers: {
              Accept: "application/json",
            },
            url: `/api/vocabularies/${vocabulary}/authoritative`,
          },
        },
      },
    };

    const suggestionApiConfig = {
      invenio: {
        requestSerializer: SuggestionRequestSerializer,
        responseSerializer: SuggestionResponseSerializer,
        suggestions: {
          // Don't need these but they are still required by Invenio
          queryField: "",
          responseField: "",
        },
      },
    };

    const searchConfig = {
      ...sources[source],
      ...{ initialQueryState: queryState },
    };

    const searchApi = new InvenioSearchApi(searchConfig.searchApi);
    const suggestionApi = new InvenioSuggestionApi({
      ...searchConfig.searchApi,
      ...suggestionApiConfig,
    });

    return (
      <OverridableContext.Provider value={overriddenComponents}>
        <ReactSearchKit
          // Suggestions are supported only by Invenio API
          suggestionApi={
            source === SearchSource.INTERNAL ? suggestionApi : null
          }
          searchApi={searchApi}
          urlHandlerApi={{ enabled: false }}
          initialQueryState={searchConfig.initialQueryState}
          {...rest}
        >
          {children}
        </ReactSearchKit>
      </OverridableContext.Provider>
    );
  }
);

/* eslint-disable react/require-default-props */
MultiSourceSearchApp.propTypes = {
  source: PropTypes.string.isRequired,
  vocabulary: PropTypes.string.isRequired,
  overriddenComponents: PropTypes.object,
  queryState: PropTypes.object,
  children: PropTypes.node,
};
/* eslint-enable react/require-default-props */

MultiSourceSearchApp.displayName = "MultiSourceSearchApp";

MultiSourceSearchApp.defaultProps = {};

export default MultiSourceSearchApp;
