import * as React from "react";
import PropTypes from "prop-types";
import { ReactSearchKit, InvenioSearchApi } from "react-searchkit";
import { OverridableContext } from "react-overridable";
import { SearchSource } from "./constants";

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
        // TODO: implement suggestions API using axios like here:
        // https://github.com/inveniosoftware/react-invenio-forms/blob/master/src/lib/forms/RemoteSelectField.js#L129
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

    const searchConfig = {
      ...sources[source],
      ...{ initialQueryState: { ...queryState } },
    };

    const searchApi = new InvenioSearchApi(searchConfig.searchApi);

    return (
      <OverridableContext.Provider value={overriddenComponents}>
        <ReactSearchKit
          searchApi={searchApi}
          urlHandlerApi={{ enabled: false }}
          initialQueryState={{
            ...searchConfig.initialQueryState,
            filters: [],
          }}
          {...rest}
        >
          {children}
        </ReactSearchKit>
      </OverridableContext.Provider>
    );
  }
);

MultiSourceSearchApp.propTypes = {
  source: PropTypes.string.isRequired,
  vocabulary: PropTypes.string.isRequired,
  overriddenComponents: PropTypes.object,
  queryState: PropTypes.object,
  children: PropTypes.node,
};

MultiSourceSearchApp.defaultProps = {};

export default MultiSourceSearchApp;
