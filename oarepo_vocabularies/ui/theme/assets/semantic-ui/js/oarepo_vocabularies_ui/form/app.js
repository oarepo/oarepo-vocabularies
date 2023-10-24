import { createFormAppInit } from "@js/oarepo_ui/forms";
import VocabularyForm from "./VocabularyForm";

export const overriddenComponents = {
    "FormApp.layout": VocabularyForm,
};

createFormAppInit(overriddenComponents);
