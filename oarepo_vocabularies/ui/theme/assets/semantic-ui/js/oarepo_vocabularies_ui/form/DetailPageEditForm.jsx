import React, { useState, useRef } from "react";
import PropTypes from "prop-types";
import * as Yup from "yup";
import {
  Container,
  Grid,
  Sticky,
  Ref,
  Input,
  Form,
  Message,
} from "semantic-ui-react";
import { BaseForm, TextField, http } from "react-invenio-forms";
import { PublishButton } from "./PublishButton";
import { FieldWithLanguageOption } from "./FieldWithLanguageOption";
import { PropFieldsComponent } from "./PropFieldsComponent";
import {
  extractVariablePart,
  transformArrayToObject,
  eliminateEmptyStringProperties,
} from "../utils";
import { useLocation } from "react-router-dom";
import { ErrorComponent } from "./Error";
import { ResetButton } from "./ResetButton";
import { MyFormSchema } from "./FormValidation";

export const DetailPageEditForm = ({
  initialValues,
  vocabulary_props,
  options,
  hasPropFields,
  apiCallUrl,
  editMode,
}) => {
  // to display errors that are consequence of API calls
  const sidebarRef = useRef(null);
  const [error, setError] = useState("");
  const location = useLocation();
  const currentPath = location.pathname;
  const vocabularyType = extractVariablePart(currentPath);
  const searchParams = new URLSearchParams(location.search);
  const newChildItem = searchParams.get("h-parent");
  const itemTitle = searchParams.get("title");

  const onSubmit = (values, formik) => {
    const preparedValues = newChildItem
      ? {
          ...values,
          title: transformArrayToObject(values.title),
          type: vocabularyType,
          props: eliminateEmptyStringProperties(values.props),
          hierarchy: { parent: newChildItem },
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
          console.log("then block");
          if (response.status >= 200 && response.status < 300) {
            formik.setSubmitting(false);
            window.location.href = currentPath.replace("/edit", "");
          }
        })
        .catch((error) => {
          formik.setSubmitting(false);
          setError(error.response.data.message);
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
          setError(error.response.data.message);
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
            {itemTitle && (
              <Message
                icon="attention"
                header="You are currently creating a sub item for item:"
                content={itemTitle}
                compact
                size="tiny"
                // don't understand how to reasonably set width for such a component in semantic!!
                style={{ width: "68%" }}
              />
            )}
            <FieldWithLanguageOption fieldPath="title" options={options} />
            {hasPropFields && (
              <PropFieldsComponent vocabularyProps={vocabulary_props} />
            )}
            <TextField fieldPath="id" label={"ID"} width={11} required />
            {error && <ErrorComponent message={error} />}
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
