import React from "react";
import { TextField, FieldLabel } from "react-invenio-forms";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import {
  IdentifiersField,
  organizationIdentifiersSchema,
} from "@nr/forms/components/IdentifiersField";

export const VocabularyFormFieldsFunders = () => {
  return (
    <React.Fragment>
      <TextField
        fieldPath="name"
        label={
          <FieldLabel htmlFor="name" icon="pencil" label={i18next.t("Name")} />
        }
        required
        placeholder={i18next.t("Name of the funder")}
      />
      <IdentifiersField
        options={organizationIdentifiersSchema}
        fieldPath="identifiers"
        selectOnBlur={false}
        validateOnBlur
        label={i18next.t("Identifiers")}
        labelIcon={null}
      />
      <TextField
        fieldPath="id"
        label={
          <FieldLabel htmlFor="id" icon="pencil" label={i18next.t("ID")} />
        }
        required
      />
    </React.Fragment>
  );
};
