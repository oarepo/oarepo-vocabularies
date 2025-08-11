import { DepositFormApp, parseFormAppConfig } from "@js/oarepo_ui/forms";
import { OARepoDepositSerializer } from "@js/oarepo_ui/api";
import React from "react";
import ReactDOM from "react-dom";
import FormAppLayout from "./FormAppLayout";
import {
  VocabularyFormControlPanel,
  VocabularyFormFields,
  VocabularyFormFieldsAwards,
  VocabularyFormFieldsNames,
  VocabularyFormFieldsFunders,
  VocabularyFormFieldsAffiliations,
} from "./components";
const config = parseFormAppConfig();
const overridableIdPrefix = config.formConfig.overridableIdPrefix;

export const componentOverrides = {
  [`${overridableIdPrefix}.FormApp.layout`]: FormAppLayout,
  [`${overridableIdPrefix}.FormFields.container`]: VocabularyFormFields,
  [`${overridableIdPrefix}.FormFields.container.awards`]:
    VocabularyFormFieldsAwards,
  [`${overridableIdPrefix}.FormFields.container.names`]:
    VocabularyFormFieldsNames,
  [`${overridableIdPrefix}.FormFields.container.funders`]:
    VocabularyFormFieldsFunders,
  [`${overridableIdPrefix}.FormFields.container.affiliations`]:
    VocabularyFormFieldsAffiliations,
  [`${overridableIdPrefix}.FormActions.container`]: VocabularyFormControlPanel,
};

const recordSerializer = new OARepoDepositSerializer(
  ["errors", "expanded"],
  ["__key"]
);

ReactDOM.render(
  <DepositFormApp
    config={config.formConfig}
    record={config.record}
    recordSerializer={recordSerializer}
    componentOverrides={componentOverrides}
  />,
  config.rootEl
);
