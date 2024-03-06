import React from "react";
import { Grid } from "semantic-ui-react";
import { TextField, MultiInput, FieldLabel } from "react-invenio-forms";
import {
  PropFieldsComponent,
  CurrentLocationInformation,
  VocabularyMultilingualInputField,
} from "../../components";
import { useLocation } from "react-router-dom";
import { useFormConfig } from "@js/oarepo_ui";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _has from "lodash/has";

export const VocabularyFormFields = () => {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");
  const {
    formConfig: { vocabularyProps },
  } = useFormConfig();
  const { formConfig } = useFormConfig();
  const editMode = _has(formConfig, "updateUrl");
  const hasPropFields = _has(vocabularyProps, "props");
  return (
    <React.Fragment>
      <Grid.Row className="rel-mb-2">
        <Grid.Column width={16}>
          <CurrentLocationInformation
            editMode={editMode}
            newChildItemParentId={newChildItemParentId}
          />
        </Grid.Column>
      </Grid.Row>

      <Grid.Column id="main-content" mobile={16} tablet={16} computer={11}>
        <VocabularyMultilingualInputField
          fieldPath="title"
          textFieldLabel={i18next.t("Title")}
          labelIcon="pencil"
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
        {hasPropFields && (
          <PropFieldsComponent vocabularyProps={vocabularyProps} />
        )}
      </Grid.Column>
    </React.Fragment>
  );
};
