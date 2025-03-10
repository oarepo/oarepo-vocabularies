import React from "react";
import { Grid } from "semantic-ui-react";
import { TextField, MultiInput, FieldLabel } from "react-invenio-forms";
import {
  PropFieldsComponent,
  VocabularyMultilingualInputField,
} from "../../components";
import { useFormConfig } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _has from "lodash/has";
import Overridable from "react-overridable";
import { buildUID } from "react-searchkit";

export const VocabularyFormFields = () => {
  const {
    formConfig: { vocabularyProps, overridableIdPrefix, vocabularyType },
  } = useFormConfig();
  const hasPropFields = _has(vocabularyProps, "props");
  return (
    <Grid.Column id="main-content" mobile={16} tablet={16} computer={11}>
      <Overridable
        id={buildUID(
          overridableIdPrefix,
          `FormFields.container.${vocabularyType}`
        )}
        vocabularyProps={vocabularyProps}
        vocabularyType={vocabularyType}
        hasPropFields={hasPropFields}
      >
        <React.Fragment>
          <VocabularyMultilingualInputField
            fieldPath="title"
            textFieldLabel={i18next.t("Title")}
            labelIcon="pencil"
            displayFirstInputRemoveButton={false}
            required={true}
          />
          <TextField
            fieldPath="id"
            label={
              <FieldLabel htmlFor="id" icon="pencil" label={i18next.t("ID")} />
            }
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
        </React.Fragment>
      </Overridable>
      {hasPropFields && (
        <PropFieldsComponent vocabularyProps={vocabularyProps} />
      )}
    </Grid.Column>
  );
};
