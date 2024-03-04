import { createFormAppInit } from "@js/oarepo_ui/forms";
import VocabularyForm from "./VocabularyForm";

export const componentOverrides = {
  "Default.Form.FormApp.layout": VocabularyForm,
};

createFormAppInit({ componentOverrides: componentOverrides });
