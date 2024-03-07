import { createFormAppInit, parseFormAppConfig } from "@js/oarepo_ui/forms";
import FormAppLayout from "./FormAppLayout";
import { VocabularyFormControlPanel, VocabularyFormFields } from "./components";
const { formConfig } = parseFormAppConfig();
const { overridableIdPrefix } = formConfig;

export const componentOverrides = {
  [`${overridableIdPrefix}.FormApp.layout`]: FormAppLayout,
  [`${overridableIdPrefix}.FormFields.container`]: VocabularyFormFields,
  [`${overridableIdPrefix}.FormActions.container`]: VocabularyFormControlPanel,
};

createFormAppInit({ componentOverrides });
