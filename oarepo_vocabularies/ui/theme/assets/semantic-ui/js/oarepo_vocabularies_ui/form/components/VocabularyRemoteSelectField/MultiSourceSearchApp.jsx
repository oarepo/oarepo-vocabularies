import * as React from "react";
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
        searchApi: {
          axios: {
            headers: {
              Accept: "application/vnd.inveniordm.v1+json",
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

export default MultiSourceSearchApp;