import { createFormAppInit, parseFormAppConfig } from "@js/oarepo_ui/forms";
import FormAppLayout from "./FormAppLayout";
import {
  VocabularyFormControlPanel,
  VocabularyFormFields,
  VocabularyFormFieldsAwards,
  VocabularyFormFieldsNames,
  VocabularyFormFieldsFunders,
  VocabularyFormFieldsAffiliations,
} from "./components";

const { formConfig } = parseFormAppConfig();
const { overridableIdPrefix } = formConfig;

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
createFormAppInit({ componentOverrides });
