import React, { useState, useRef } from "react";
import PropTypes from "prop-types";
import { Container, Grid, Sticky, Ref } from "semantic-ui-react";
import { BaseForm, TextField, http } from "react-invenio-forms";
import { PublishButton } from "./components/PublishButton";
import { FieldWithLanguageOption } from "./components/FieldWithLanguageOption";
import { PropFieldsComponent } from "./components/PropFieldsComponent";
import {
  extractVariablePart,
  transformArrayToObject,
  eliminateEmptyStringProperties,
} from "../utils";
import { useLocation } from "react-router-dom";
import { ErrorComponent } from "./components/Error";
import { ResetButton } from "./components/ResetButton";
import { MyFormSchema } from "./FormValidation";
// import { SelectParentItem } from "./SelectParentItem";
import { FormikStateLogger } from "./components/FormikStateLogger";
import { CurrentLocationInformation } from "./components/CurrentLocationInformation";

export const DetailPageEditForm = ({
  initialValues,
  vocabulary_props,
  options,
  hasPropFields,
  apiCallUrl,
  editMode,
  vocabularyRecord,
}) => {
  // to display errors that are consequence of API calls
  const sidebarRef = useRef(null);
  const [error, setError] = useState({});
  const location = useLocation();
  const currentPath = location.pathname;
  const vocabularyType = extractVariablePart(currentPath);
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");

  const onSubmit = (values, formik) => {
    const preparedValues = newChildItemParentId
      ? {
          ...values,
          title: transformArrayToObject(values.title),
          type: vocabularyType,
          props: eliminateEmptyStringProperties(values.props),
          hierarchy: { parent: newChildItemParentId },
        }
      : {
          ...values,
          title: transformArrayToObject(values.title),
          type: vocabularyType,
          props: eliminateEmptyStringProperties(values.props),
        };

    if (editMode) {
      http
        .put(apiCallUrl, preparedValues)
        .then((response) => {
          setError("");
          if (response.status >= 200 && response.status < 300) {
            formik.setSubmitting(false);
            window.location.href = currentPath.replace("/edit", "");
          }
        })
        .catch((error) => {
          formik.setSubmitting(false);
          setError(error.response.data);
        });
    } else {
      http
        .post(apiCallUrl, preparedValues)
        .then((response) => {
          setError("");
          if (response.status >= 200 && response.status < 300) {
            formik.setSubmitting(false);
            window.location.href = currentPath.replace("_new", values.id);
          }
        })
        .catch((error) => {
          formik.setSubmitting(false);
          setError(error.response.data);
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
        <Grid>
          <Grid.Column mobile={16} tablet={16} computer={12}>
            <CurrentLocationInformation
              vocabularyRecord={vocabularyRecord}
              editMode={editMode}
              newChildItemParentId={newChildItemParentId}
            />
            <FieldWithLanguageOption fieldPath="title" options={options} />
            {hasPropFields && (
              <PropFieldsComponent vocabularyProps={vocabulary_props} />
            )}
            <TextField fieldPath="id" label={"ID"} width={11} required />
            {/* <SelectParentItem vocabularyRecord={vocabularyRecord} /> */}
            <FormikStateLogger />
            {error.message && <ErrorComponent error={error} />}
          </Grid.Column>
          <Ref innerRef={sidebarRef}>
            <Grid.Column mobile={16} tablet={16} computer={4}>
              <Sticky context={sidebarRef} offset={20}>
                <PublishButton />
                <ResetButton />
              </Sticky>
            </Grid.Column>
          </Ref>
        </Grid>
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
