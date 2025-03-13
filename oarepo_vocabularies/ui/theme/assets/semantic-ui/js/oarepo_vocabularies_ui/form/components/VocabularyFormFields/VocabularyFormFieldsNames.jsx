import React from "react";
import { TextField, FieldLabel, RemoteSelectField } from "react-invenio-forms";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import {
  IdentifiersField,
  personIdentifiersSchema,
} from "@nr/forms/components/IdentifiersField";
import { getIn, useFormikContext } from "formik";
import PropTypes from "prop-types";
import { Trans } from "react-i18next";
import { useSetIdBasedOnIdentifier } from "./hooks";

const serializeAffiliations = (affiliations) =>
  affiliations.map((affiliation) => ({
    value: affiliation.id,
    text: affiliation.name,
    key: affiliation.id,
  }));

export const VocabularyFormFieldsNames = ({ editMode }) => {
  const { values } = useFormikContext();
  useSetIdBasedOnIdentifier(editMode);
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
        placeholder={i18next.t("Family name")}
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
        placeholder={i18next.t("First name")}
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
      <Trans i18next={i18next}>
        <span className="helpText">
          If you cannot find an appropriate affiliation, you can create one{" "}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="/vocabularies/affiliations/_new"
          >
            here.
          </a>
        </span>
      </Trans>
      <TextField
        fieldPath="id"
        label={
          <FieldLabel htmlFor="id" icon="pencil" label={i18next.t("ID")} />
        }
        placeholder={i18next.t(
          "Use personal identifier eg orcid:0000-0001-9718-6515. If you dont provide ID, random ID will be assigned."
        )}
        required
      />
    </React.Fragment>
  );
};

VocabularyFormFieldsNames.propTypes = {
  editMode: PropTypes.bool,
};
