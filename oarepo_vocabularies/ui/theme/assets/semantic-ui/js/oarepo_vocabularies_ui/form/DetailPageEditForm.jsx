import React from "react";
import PropTypes from "prop-types";
import * as Yup from "yup";
import { Container } from "semantic-ui-react";
import { BaseForm, TextField, http } from "react-invenio-forms";
import { PublishButton } from "./PublishButton";
import { useFormikContext } from "formik";
import { FieldWithLanguageOption } from "./FieldWithLanguageOption";
import { PropFieldsComponent } from "./PropFieldsComponent";
import {
  extractVariablePart,
  transformArrayToObject,
  checkDuplicateLanguage,
} from "../util";
import { useLocation } from "react-router-dom";

const FormikStateLogger = () => {
  const state = useFormikContext();
  return <pre>{JSON.stringify(state, null, 2)}</pre>;
};

const MyFormSchema = Yup.object().shape({
  title: Yup.array()
    .of(
      Yup.object().shape({
        language: Yup.string().required("required"), // these constraints take precedence
        title: Yup.string().required("required"), // these constraints take precedence
      })
    )
    .test(
      "same language",
      (value) => {
        console.log(value.value);
        return [
          value.value.map((item) => ({
            language: "You must not have two same languages",
          })),
        ];
      },
      (value, context) => {
        console.log(value, context);
        console.log(checkDuplicateLanguage(value));
        return checkDuplicateLanguage(value);
      }
    ),

  ICO: Yup.string().length(8, "musi byt presne 8"),
  RID: Yup.string().length(5),
  id: Yup.string().required("required"),
});

export const DetailPageEditForm = ({
  initialValues,
  vocabulary_props,
  options,
  hasPropFields,
  apiCallUrl,
  editMode,
}) => {
  const currentPath = useLocation().pathname;
  const vocabularyType = extractVariablePart(currentPath);
  const onSubmit = (values, formik) => {
    console.log(formik);
    const preparedValues = {
      ...values,
      title: transformArrayToObject(values.title),
      type: vocabularyType,
    };
    if (editMode) {
      http
        .put(apiCallUrl, preparedValues)
        .then((response) => {
          if (response.status >= 200 && response.status < 300) {
            formik.setSubmitting(false);
            window.location.href = currentPath.replace("/edit", "");
          }
        })
        .catch((error) => {
          // Handle the error
          console.error(error);
        });
    } else {
      http
        .post(apiCallUrl, preparedValues)
        .then((response) => {
          if (response.status >= 200 && response.status < 300) {
            formik.setSubmitting(false);
            window.location.href = currentPath.replace("_new", values.id);
          }
        })
        .catch((error) => {
          // Handle the error
          console.error(error);
        });
    }
  };
  return (
    <Container>
      <BaseForm
        onSubmit={onSubmit}
        // onError={this.onError}
        formik={{
          initialValues: initialValues,
          validationSchema: MyFormSchema,
          validateOnChange: false,
          validateOnBlur: false,
        }}
      >
        <FieldWithLanguageOption fieldPath="title" options={options} />
        {hasPropFields && (
          <PropFieldsComponent vocabularyProps={vocabulary_props} />
        )}
        <TextField fieldPath="id" label={"ID"} width={11} required />
        <FormikStateLogger />
        <PublishButton />
      </BaseForm>
    </Container>
  );
};

const TitlePropType = PropTypes.shape({
  language: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
});

DetailPageEditForm.propTypes = {
  initialValues: PropTypes.shape({
    title: PropTypes.arrayOf(TitlePropType).isRequired,
    ICO: PropTypes.string,
    RID: PropTypes.string,
    acronym: PropTypes.string,
    nameType: PropTypes.string,
  }),
  vocabulary_props: PropTypes.object,
  hasPropFields: PropTypes.bool,
  options: PropTypes.shape({
    languages: PropTypes.arrayOf(
      PropTypes.shape({
        text: PropTypes.string.isRequired,
        value: PropTypes.string.isRequired,
      })
    ),
  }),
};
