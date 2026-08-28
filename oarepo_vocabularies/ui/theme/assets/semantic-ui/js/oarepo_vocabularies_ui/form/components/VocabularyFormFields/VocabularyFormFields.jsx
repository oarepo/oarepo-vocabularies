import React from "react";
import { TextField, MultiInput, FieldLabel } from "react-invenio-forms";
import {
  PropFieldsComponent,
  VocabularyMultilingualInputField,
  GenericIdentifiersField,
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
  const isUpdateForm = _has(config, "updateUrl");
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
        <GenericIdentifiersField
          fieldPath="identifiers"
          selectOnBlur={false}
          validateOnBlur
          label={i18next.t("Identifiers")}
          labelIcon={null}
          addButtonLabel={i18next.t("Add identifier")}
          identifierPlaceholder={i18next.t("Identifier value")}
          helpText={i18next.t(
            "Add external identifiers that this vocabulary item maps to. The mapping is one-way: the external identifier may not map back to this item."
          )}
        />
        <GenericIdentifiersField
          fieldPath="crosswalks"
          selectOnBlur={false}
          validateOnBlur
          label={i18next.t("Crosswalks")}
          labelIcon={null}
          addButtonLabel={i18next.t("Add crosswalk")}
          identifierPlaceholder={i18next.t("Crosswalk value")}
          helpText={i18next.t(
            "Add crosswalk mappings from vocabulary items in other systems to this item. Mappings are one-way: the external item maps to this item, but this item may not fully map back to it."
          )}
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
