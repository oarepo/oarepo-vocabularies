import React from "react";
import PropTypes from "prop-types";
import { DetailPageEditForm } from "./DetailPageEditForm";
import { translateObjectToArray, clearObjectValues } from "../utils";
import _ from "lodash";

const options = {
  languages: [
    { text: "cs", value: "cs" },
    { text: "en", value: "en" },
    { text: "de", value: "de" },
  ],
};

const VocabularyForm = ({ vocabularyRecord, formConfig }) => {
  const { vocabulary_props } = formConfig;
  const editMode = _.has(formConfig, "updateUrl");
  const hasPropFields = !_.isEmpty(vocabulary_props);
  const apiCallUrl = editMode ? formConfig.updateUrl : formConfig.createUrl;

  const editModeAndProps = editMode
    ? vocabularyRecord.props
    : clearObjectValues({ ...vocabulary_props.props });

  const propFieldsWithValues = hasPropFields ? editModeAndProps : {};

  const initialValues = editMode
    ? {
        title: translateObjectToArray(vocabularyRecord.title),
        props: propFieldsWithValues,
        id: vocabularyRecord.id,
        // "h-parent": vocabularyRecord.hierarchy.parent ? { key: "amu", value: "amu", text: "amu" } : { key: "amu", value: "amu", text: "amu" },
      }
    : {
        title: [{ language: "cs", title: "" }],
        props: propFieldsWithValues,
        id: "",
      };

  return (
    <DetailPageEditForm
      initialValues={initialValues}
      formConfig={formConfig}
      options={options}
      hasPropFields={hasPropFields}
      vocabulary_props={vocabulary_props}
      apiCallUrl={apiCallUrl}
      editMode={editMode}
      vocabularyRecord={vocabularyRecord}
    />
  );
};

VocabularyForm.propTypes = {
  vocabularyRecord: PropTypes.object.isRequired,
  formConfig: PropTypes.object.isRequired,
};

export default VocabularyForm;
