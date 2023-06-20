/*
This is the registration file for custom components. The components should not be included here,
but only referenced. The sample component below can be used to start up working on your own custom
component.
*/
/*

In the sample-component.js you can define your own javascript functions etc for your custom component.
Then import the file here

import "./sample-component.js"
*/

// This file will import the css templates for your custom components
import "../../less/oarepo_vocabularies_ui/custom-components.less";
import React from "react";
import ReactDOM from "react-dom";
import { createSearchAppInit } from "@js/invenio_search_ui";

const defaultComponents = {};

const reactApp = createSearchAppInit(
  defaultComponents,
  false,
  "invenio-search-config",
  true
);

const MyReactApp = () => <div>This is my react app</div>;

document.addEventListener("DOMContentLoaded", function () {
  const rootElement = document.getElementById("root");
  const searchAppElements = document.querySelectorAll(
    `[data-invenio-search-config]`
  );
  console.log(searchAppElements);
  document.getElementById("test").addEventListener("click", () => {
    reactApp(searchAppElements[0]);
  });
});
