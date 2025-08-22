import React from "react";
import { TextField, MultiInput, FieldLabel } from "react-invenio-forms";
import {
  PropFieldsComponent,
  VocabularyMultilingualInputField,
} from "../../components";
import { useFormConfig } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _has from "lodash/has";
import Overridable from "react-overridable";
import { buildUID } from "react-searchkit";

export const VocabularyFormFields = () => {
  const { formConfig } = useFormConfig();
  const { vocabularyProps, overridableIdPrefix, vocabularyType } = formConfig;

  const hasPropFields = _has(vocabularyProps, "props");
  const isUpdateForm = _has(formConfig, "updateUrl");
  return (
    <Overridable
      id={buildUID(
        overridableIdPrefix,
        `FormFields.container.${vocabularyType}`
      )}
      vocabularyProps={vocabularyProps}
      vocabularyType={vocabularyType}
      hasPropFields={hasPropFields}
      isUpdateForm={isUpdateForm}
    >
      <React.Fragment>
        <VocabularyMultilingualInputField
          fieldPath="title"
          textFieldLabel={i18next.t("Title")}
          labelIcon="pencil"
          displayFirstInputRemoveButton={false}
          required
        />
        <TextField
          fieldPath="id"
          label={
            <FieldLabel htmlFor="id" icon="pencil" label={i18next.t("ID")} />
          }
          placeholder={i18next.t(
            "If you dont provide ID, random ID will be assigned."
          )}
          required
        />
        <MultiInput
          fieldPath="tags"
          label={i18next.t("Tags")}
          icon="tags"
          placeholder={i18next.t("Enter one or more tags.")}
          required={false}
        />
        <TextField
          fieldPath="icon"
          label={
            <FieldLabel
              htmlFor="icon"
              icon="pencil"
              label={i18next.t("Icon")}
            />
          }
          placeholder={i18next.t(
            "URL for the icon describing the vocabulary item."
          )}
        />
        {hasPropFields && (
          <PropFieldsComponent vocabularyProps={vocabularyProps} />
        )}
      </React.Fragment>
    </Overridable>
  );
};
