import React, { useEffect } from "react";
import { TextField, FieldLabel, RemoteSelectField } from "react-invenio-forms";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import {
  IdentifiersField,
  personIdentifiersSchema,
} from "@nr/forms/components/IdentifiersField";
import { getIn, useFormikContext } from "formik";
import { useFormConfig } from "@js/oarepo_ui/forms";
import _has from "lodash/has";

const serializeAffiliations = (affiliations) =>
  affiliations.map((affiliation) => ({
    value: affiliation.id,
    text: affiliation.name,
    key: affiliation.id,
  }));

export const VocabularyFormFieldsNames = () => {
  const { values, setFieldValue } = useFormikContext();
  const { formConfig } = useFormConfig();
  const editMode = _has(formConfig, "updateUrl");

  const { scheme, identifier } = getIn(values, "identifiers.0", "");
  useEffect(() => {
    if (editMode) {
      return;
    }
    if (scheme && identifier) {
      setFieldValue("id", `${scheme}:${identifier}`);
    }
    if (!scheme && !identifier) {
      setFieldValue("id", "");
    }
  }, [scheme, identifier, setFieldValue, editMode]);
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
        placeholder={i18next.t(
          "Use first identifier and its scheme as id (scheme:identifier). Otherwise random id will be assigned."
        )}
        required
      />
    </React.Fragment>
  );
};
