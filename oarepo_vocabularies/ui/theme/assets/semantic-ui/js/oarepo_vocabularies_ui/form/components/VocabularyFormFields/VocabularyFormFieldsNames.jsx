import React from "react";
import { TextField, FieldLabel, RemoteSelectField } from "react-invenio-forms";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import {
  IdentifiersField,
  personIdentifiersSchema,
} from "@nr/forms/components/IdentifiersField";
import { getIn, useFormikContext } from "formik";

const serializeAffiliations = (affiliations) =>
  affiliations.map((affiliation) => ({
    value: affiliation.id,
    text: affiliation.name,
    key: affiliation.id,
  }));

export const VocabularyFormFieldsNames = () => {
  const { values } = useFormikContext();
  const affiliationsFieldPath = "affiliations";
  return (
    <React.Fragment>
      <TextField
        fieldPath="family_name"
        label={
          <FieldLabel
            htmlFor="family_name"
            icon="pencil"
            label={i18next.t("Family name")}
          />
        }
        required
      />
      <TextField
        fieldPath="given_name"
        label={
          <FieldLabel
            htmlFor="given_name"
            icon="pencil"
            label={i18next.t("First name")}
          />
        }
        required
      />
      <IdentifiersField
        options={personIdentifiersSchema}
        fieldPath="identifiers"
        selectOnBlur={false}
        validateOnBlur
        label={i18next.t("Identifiers")}
        labelIcon={null}
      />
      <RemoteSelectField
        fieldPath={affiliationsFieldPath}
        suggestionAPIUrl="/api/affiliations"
        suggestionAPIHeaders={{
          Accept: "application/json",
        }}
        initialSuggestions={getIn(values, affiliationsFieldPath, [])}
        serializeSuggestions={serializeAffiliations}
        placeholder={i18next.t("Search for affiliations..")}
        label={
          <FieldLabel
            htmlFor={`${affiliationsFieldPath}.name`}
            label={i18next.t("Affiliations")}
          />
        }
        noQueryMessage={i18next.t("Search for affiliations..")}
        clearable
        multiple
        onValueChange={({ formikProps }, selectedSuggestions) => {
          const formikSuggestions = selectedSuggestions.map((suggestion) => ({
            id: suggestion.value,
            name: suggestion.text,
          }));
          formikProps.form.setFieldValue(
            affiliationsFieldPath,
            formikSuggestions
          );
        }}
        value={getIn(values, affiliationsFieldPath, []).map(
          (val) => val.id || val.text || val.name
        )}
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
