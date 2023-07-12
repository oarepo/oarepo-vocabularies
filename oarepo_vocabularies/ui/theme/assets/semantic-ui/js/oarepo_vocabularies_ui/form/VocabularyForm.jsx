import React from "react";
import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import { DetailPageEditForm } from "./DetailPageEditForm";
import { translateObjectToArray, clearObjectValues } from "../utils";
import _ from "lodash";

const FormikStateLogger = () => {
  const state = useFormikContext();
  return <pre>{JSON.stringify(state, null, 2)}</pre>;
};

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
    />
  );
};

VocabularyForm.propTypes = {
  vocabularyRecord: PropTypes.object.isRequired,
  formConfig: PropTypes.object.isRequired,
};

export default VocabularyForm;
