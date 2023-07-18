import React from "react";
import { createFormAppInit, useFormConfig } from "@js/oarepo_ui/forms";
import VocabularyForm from "./VocabularyForm";

// TODO(ducica): Provide your form layout here
// To access the form config values, use the following hook in your components:
//
// import {useFormConfig} from '@js/oarepo_ui/forms'
// const {record, formConfig, recordPermissions} = useFormConfig()

const ExampleVocabularyFormLayout = () => {
  const { record, formConfig, recordPermissions } = useFormConfig();
  return (
    <div>
      <div>
        <p>Your example vocabulary form here</p>
      </div>
      <div>
        <h2>Record data</h2>
        <pre>{JSON.stringify(record, null, 4)}</pre>
        <h2>Form Config</h2>
        <pre>{JSON.stringify(formConfig, null, 4)}</pre>
        <h2>Record permissions</h2>
        <pre>{JSON.stringify(recordPermissions, null, 4)}</pre>
      </div>
    </div>
  );
};

export const overriddenComponents = {
  "FormApp.layout": VocabularyForm,
};

createFormAppInit(overriddenComponents);

// import React from "react";
// import ReactDOM from "react-dom";
// import { getInputFromDOM } from "../utils";
// import { OverridableContext, overrideStore } from "react-overridable";
// import VocabularyForm from "./VocabularyForm";
// import { BrowserRouter as Router } from "react-router-dom";

// const vocabularyRecord = getInputFromDOM("vocabulary-record");
// const formConfig = getInputFromDOM("form-config");
// const appRoot = document.getElementById("vocabulary-form");

// // should recieve camelCased properties from the server i.e. formConfig contains vocabulary_props

// export const overriddenComponents = {};
// console.log(
//   "[vocabularyRecord]:",
//   vocabularyRecord,
//   "\n[formConfig]",
//   formConfig
// );
// // TODO: remove when not needed for development
// console.debug(
//   "[vocabularyRecord]:",
//   vocabularyRecord,
//   "\n[formConfig]",
//   formConfig
// );

// ReactDOM.render(
//   <OverridableContext.Provider value={overriddenComponents}>
//     <Router>
//       <VocabularyForm
//         vocabularyRecord={vocabularyRecord}
//         formConfig={formConfig}
//       />
//     </Router>
//   </OverridableContext.Provider>,
//   appRoot
// );
