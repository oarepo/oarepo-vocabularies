import React from "react";
import { TextField, FieldLabel } from "react-invenio-forms";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import {
  IdentifiersField,
  organizationIdentifiersSchema,
} from "@js/oarepo_ui/forms";
import { VocabularyMultilingualInputField } from "../VocabularyMultilingualInputField";
import PropTypes from "prop-types";
import { useSetIdBasedOnIdentifier } from "./hooks";

export const VocabularyFormFieldsFunders = ({ isUpdateForm }) => {
  useSetIdBasedOnIdentifier(isUpdateForm);
  return (
    <React.Fragment>
      <TextField
        fieldPath="name"
        label={
          <FieldLabel
            htmlFor="name"
            icon="pencil"
            label={i18next.t("Funder name")}
          />
        }
        required
        placeholder={i18next.t("Name of the funder")}
      />
      <VocabularyMultilingualInputField
        fieldPath="title"
        textFieldLabel={i18next.t("Title")}
        labelIcon="pencil"
        displayFirstInputRemoveButton
        required
        newItemInitialValue={{}}
        helpText={i18next.t(
          "Here you can provide the funder name in multiple languages. You can also include the one provided in the 'Name' field with appropriate language selected."
        )}
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
        placeholder={i18next.t(
          "Use personal identifier eg ror:05pq4yn02. If you dont provide ID, random ID will be assigned."
        )}
        required
      />
    </React.Fragment>
  );
};

VocabularyFormFieldsFunders.propTypes = {
  isUpdateForm: PropTypes.bool.isRequired,
};
