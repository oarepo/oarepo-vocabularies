import FormAppLayout from "./FormAppLayout";
import {
  VocabularyFormFieldsAwards,
  VocabularyFormFieldsNames,
  VocabularyFormFieldsFunders,
  VocabularyFormFieldsAffiliations,
} from "./components";
import { DepositFormApp, parseFormAppConfig } from "@js/oarepo_ui/forms";
import React from "react";
import { OARepoDepositSerializer } from "@js/oarepo_ui/api";

import ReactDOM from "react-dom";

const recordSerializer = new OARepoDepositSerializer(
  ["errors", "expanded"],
  ["__key"]
);

const { rootEl, config, ...rest } = parseFormAppConfig();
const { overridableIdPrefix } = config;

export const componentOverrides = {
  [`${overridableIdPrefix}.FormApp.layout`]: FormAppLayout,
  [`${overridableIdPrefix}.FormFields.container.awards`]:
    VocabularyFormFieldsAwards,
  [`${overridableIdPrefix}.FormFields.container.names`]:
    VocabularyFormFieldsNames,
  [`${overridableIdPrefix}.FormFields.container.funders`]:
    VocabularyFormFieldsFunders,
  [`${overridableIdPrefix}.FormFields.container.affiliations`]:
    VocabularyFormFieldsAffiliations,
};

ReactDOM.render(
  <DepositFormApp
    config={config}
    {...rest}
    recordSerializer={recordSerializer}
    componentOverrides={componentOverrides}
  />,
  rootEl
);
