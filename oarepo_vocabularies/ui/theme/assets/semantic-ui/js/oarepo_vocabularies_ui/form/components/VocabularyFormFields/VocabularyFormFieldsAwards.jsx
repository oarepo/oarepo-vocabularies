import React, { useEffect } from "react";
import { TextField, FieldLabel, RemoteSelectField } from "react-invenio-forms";
import { VocabularyMultilingualInputField } from "../VocabularyMultilingualInputField";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { getIn, useFormikContext } from "formik";
import PropTypes from "prop-types";
import { Trans } from "react-i18next";

export const VocabularyFormFieldsAwards = ({ isUpdateForm }) => {
  const { values, setFieldValue } = useFormikContext();

  const funder = getIn(values, "funder", {});
  const awardNumber = getIn(values, "number", "");
  useEffect(() => {
    if (isUpdateForm) {
      return;
    }
    if (funder?.id && awardNumber) {
      setFieldValue("id", `${funder.id}:${awardNumber}`);
    }
  }, [funder.id, awardNumber, setFieldValue, isUpdateForm]);
  return (
    <React.Fragment>
      <TextField
        fieldPath="number"
        label={
          <FieldLabel
            htmlFor="number"
            icon="pencil"
            label={i18next.t("Number")}
          />
        }
        placeholder={i18next.t("Award number i.e. 754657")}
        required
      />
      <VocabularyMultilingualInputField
        fieldPath="title"
        textFieldLabel={i18next.t("Title")}
        labelIcon="pencil"
        displayFirstInputRemoveButton={false}
        newItemInitialValue={{}}
        helpText={i18next.t(
          "You can provide award name in multiple languages."
        )}
      />
      <RemoteSelectField
        fieldPath="funder.id"
        suggestionAPIUrl="/api/funders"
        suggestionAPIHeaders={{
          Accept: "application/vnd.inveniordm.v1+json",
        }}
        initialSuggestions={funder.id ? [funder] : []}
        placeholder={i18next.t("Search for a funder by name")}
        serializeSuggestions={(funders) => {
          return funders.map((funder) => ({
            text: funder.name,
            value: funder.id,
            key: funder.id,
          }));
        }}
        label={
          <FieldLabel
            htmlFor="funder.id"
            icon="pencil"
            label={i18next.t("Funder")}
          />
        }
        noQueryMessage={i18next.t("Search for funder...")}
        required
        search={(options) => options}
        onValueChange={({ formikProps }, selectedFundersArray) => {
          if (selectedFundersArray.length === 1) {
            const selectedFunder = selectedFundersArray[0];
            if (selectedFunder) {
              formikProps.form.setFieldValue("funder", {
                id: selectedFunder.value,
                name: selectedFunder.text,
              });
            }
          }
        }}
      />
      <Trans i18n={i18next}>
        <span className="helpText">
          If you cannot find an appropriate funder, you can create one{" "}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="/vocabularies/funders/_new"
          >
            here.
          </a>
        </span>
      </Trans>
      <TextField
        fieldPath="program"
        label={
          <FieldLabel
            htmlFor="program"
            icon="pencil"
            label={i18next.t("Programme")}
          />
        }
      />
      <TextField
        fieldPath="acronym"
        label={
          <FieldLabel
            htmlFor="acronym"
            icon="pencil"
            label={i18next.t("Acronym")}
          />
        }
        placeholder={i18next.t("ULAKBIM")}
      />
      <TextField
        fieldPath="id"
        label={
          <FieldLabel htmlFor="id" icon="pencil" label={i18next.t("ID")} />
        }
        required
        placeholder={i18next.t(
          "Use format: FunderID:Award Number i.e. AV0:754657. If you dont provide ID, random ID will be assigned."
        )}
      />
    </React.Fragment>
  );
};

VocabularyFormFieldsAwards.propTypes = {
  isUpdateForm: PropTypes.bool.isRequired,
};
