// SPDX-FileCopyrightText: 2024-2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

import React from "react";
import { TextField, MultiInput, FieldLabel } from "react-invenio-forms";
import {
  PropFieldsComponent,
  VocabularyMultilingualInputField,
  VocabularyMappingsField,
} from "../../components";
import { useFormConfig } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _has from "lodash/has";
import Overridable from "react-overridable";
import { buildUID } from "react-searchkit";

export const VocabularyFormFields = () => {
  const { config } = useFormConfig();
  const { vocabularyProps, overridableIdPrefix, vocabularyType } = config;

  const hasPropFields = _has(vocabularyProps, "props");
  const isUpdateForm = !config.createUrl;
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
        <VocabularyMultilingualInputField
          fieldPath="description"
          label={i18next.t("Description")}
          textFieldLabel={i18next.t("Description")}
          labelIcon="pencil"
          newItemInitialValue={{}}
        />
        <TextField
          fieldPath="id"
          label={
            <FieldLabel htmlFor="id" icon="pencil" label={i18next.t("ID")} />
          }
          placeholder={i18next.t(
            "If you dont provide ID, random ID will be assigned."
          )}
          // changing the id of an existing item would break records referencing it
          disabled={isUpdateForm}
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
        <PropFieldsComponent vocabularyProps={vocabularyProps} />
        <VocabularyMappingsField />
      </React.Fragment>
    </Overridable>
  );
};
