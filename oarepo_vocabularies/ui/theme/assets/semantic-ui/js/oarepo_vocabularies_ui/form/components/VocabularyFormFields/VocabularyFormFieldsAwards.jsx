import React from "react";
import { TextField, FieldLabel, RemoteSelectField } from "react-invenio-forms";
import { VocabularyMultilingualInputField } from "..";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { getIn, useFormikContext } from "formik";

export const VocabularyFormFieldsAwards = () => {
  const { values } = useFormikContext();
  const funder = getIn(values, "funder", {});
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
        placeholder={i18next.t("Award number i.e. 1A8238")}
        required
      />
      <VocabularyMultilingualInputField
        fieldPath="title"
        textFieldLabel={i18next.t("Title")}
        labelIcon="pencil"
        displayFirstInputRemoveButton={true}
        newItemInitialValue={{}}
      />
      <RemoteSelectField
        fieldPath="funder.id"
        suggestionAPIUrl="/api/funders"
        suggestionAPIHeaders={{
          Accept: "application/vnd.inveniordm.v1+json",
        }}
        initialSuggestions={[funder]}
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
        allowAdditions={false}
        multiple={false}
        selectOnBlur={false}
        selectOnNavigation={false}
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
        fieldPath="id"
        label={
          <FieldLabel htmlFor="id" icon="pencil" label={i18next.t("ID")} />
        }
        required
      />
    </React.Fragment>
  );
};
