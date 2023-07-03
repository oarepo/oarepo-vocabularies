import React from "react";
import PropTypes from "prop-types";
import * as Yup from "yup";
import { Header, Message, Container, Button, Form } from "semantic-ui-react";
import { useFormikContext, Field } from "formik";
import { FieldWithLanguageOption } from "./FieldWithLanguageOption";
import { DetailPageEditForm } from "./DetailPageEditForm";
import { translateObjectToArray, clearObjectValues } from "../util";
import _ from "lodash";

const FormikStateLogger = () => {
  const state = useFormikContext();
  return <pre>{JSON.stringify(state, null, 2)}</pre>;
};

// const formConfig = {
//   props: {
//     alpha3CodeENG: "abk",
//   },
//   title: {
//     cs: "abcházština",
//     en: "Abkhazian",
//   },
//   options: {
//     languages: [
//       { text: "cs", value: "cs" },
//       { text: "en", value: "en" },
//       { text: "de", value: "de" },
//     ],
//   },
//   editMode: true,
// };
// should get options also as part of config from backend?
const options = {
  languages: [
    { text: "cs", value: "cs" },
    { text: "en", value: "en" },
    { text: "de", value: "de" },
  ],
};
const VocabularyForm = ({ vocabularyRecord, formConfig }) => {
  console.log(formConfig);
  const { vocabulary_props } = formConfig;
  const editMode = _.has(formConfig, "updateUrl");
  const hasPropFields = !_.isEmpty(vocabulary_props);
  const apiCallUrl = editMode
    ? formConfig.updateUrl.replace("https://127.0.0.1:5000", "")
    : formConfig.createUrl;
  const propFieldsWithValues = hasPropFields
    ? editMode
      ? vocabularyRecord.props
      : clearObjectValues(vocabulary_props)
    : {};

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
  console.log(initialValues);

  const onError = (error) => {
    console.log("Server Error", error);
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

export default VocabularyForm;
