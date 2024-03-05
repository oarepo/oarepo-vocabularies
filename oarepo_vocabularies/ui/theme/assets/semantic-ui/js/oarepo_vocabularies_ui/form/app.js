import { createFormAppInit, parseFormAppConfig } from "@js/oarepo_ui/forms";
import VocabularyForm from "./VocabularyForm";
const { formConfig } = parseFormAppConfig();
const { overridableIdPrefix } = formConfig;

export const componentOverrides = {
  [`${overridableIdPrefix}.FormApp.layout`]: VocabularyForm,
};

createFormAppInit({ componentOverrides: componentOverrides });
