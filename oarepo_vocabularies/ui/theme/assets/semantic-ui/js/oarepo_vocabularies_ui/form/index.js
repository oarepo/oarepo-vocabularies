import React from "react";
import ReactDOM from "react-dom";
import { getInputFromDOM } from "../utils";
import { OverridableContext, overrideStore } from "react-overridable";
import VocabularyForm from "./VocabularyForm";
import { BrowserRouter as Router } from "react-router-dom";

const vocabularyRecord = getInputFromDOM("vocabulary-record");
const formConfig = getInputFromDOM("form-config");
const appRoot = document.getElementById("vocabulary-form");

// should recieve camelCased properties from the server i.e. formConfig contains vocabulary_props

export const overriddenComponents = {};
console.log(
  "[vocabularyRecord]:",
  vocabularyRecord,
  "\n[formConfig]",
  formConfig
);
// TODO: remove when not needed for development
console.debug(
  "[vocabularyRecord]:",
  vocabularyRecord,
  "\n[formConfig]",
  formConfig
);

ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <Router>
      <VocabularyForm
        vocabularyRecord={vocabularyRecord}
        formConfig={formConfig}
      />
    </Router>
  </OverridableContext.Provider>,
  appRoot
);
