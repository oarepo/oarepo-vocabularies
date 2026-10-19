// SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

import React from "react";
import ReactDOM from "react-dom";
import _camelCase from "lodash/camelCase";
import { App } from "./DetailSearchApp";
import { ExportDropdown } from "@js/invenio_app_rdm/landing_page/ExportDropdown";

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

  const recordExportDownloadDiv = document.getElementById(
    "recordExportDownload"
  );
  if (recordExportDownloadDiv) {
    ReactDOM.render(
      <ExportDropdown
        formats={JSON.parse(recordExportDownloadDiv.dataset.formats)}
      />,
      recordExportDownloadDiv
    );
  }
});
