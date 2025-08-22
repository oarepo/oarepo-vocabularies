import React from "react";
import ReactDOM from "react-dom";
import _camelCase from "lodash/camelCase";
import { App } from "./DetailSearchApp";

document.addEventListener("DOMContentLoaded", function () {
  const searchAppElement = document.querySelector(
    `[data-invenio-search-config]`
  );

  if (searchAppElement) {
    const initialAppConfig = JSON.parse(
      searchAppElement.dataset[_camelCase("invenio-search-config")]
    );

    const uiLinksConfig = JSON.parse(
      searchAppElement.dataset[_camelCase("ui-links")]
    );

    initialAppConfig.uiLinks = uiLinksConfig;

    ReactDOM.render(<App appConfig={initialAppConfig} />, searchAppElement);
  }
});
