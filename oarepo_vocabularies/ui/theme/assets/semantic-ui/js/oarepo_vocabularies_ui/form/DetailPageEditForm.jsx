import React, { useState, useRef } from "react";
import PropTypes from "prop-types";
import { Container, Grid, Sticky, Ref } from "semantic-ui-react";
import { BaseForm, TextField, http } from "react-invenio-forms";
import { PublishButton } from "./components/PublishButton";
import { MultiLingualTextInput } from "./components/MultiLingualTextInput";
import { PropFieldsComponent } from "./components/PropFieldsComponent";
import { extractVariablePart, transformArrayToObject } from "../utils";
import { useLocation } from "react-router-dom";
import { ErrorComponent } from "./components/Error";
import { ResetButton } from "./components/ResetButton";
import { VocabularyFormSchema } from "./VocabularyFormSchema";
import { FormikStateLogger } from "./components/FormikStateLogger";
import { CurrentLocationInformation } from "./components/CurrentLocationInformation";
import { useFormConfig } from "@js/oarepo_ui/forms";
import _omitBy from "lodash/omitBy";
import Overridable from "react-overridable";

const eliminateEmptyStringProperties = (obj) => {
  return _omitBy(obj, (value) => value === "");
};

export const DetailPageEditForm = ({
  initialValues,
  options,
  hasPropFields,
  editMode,
  apiCallUrl,
}) => {
  const {
    record,
    formConfig: { vocabularyProps },
  } = useFormConfig();
  console.log("dsadsada");
  // to display errors that are consequence of API calls
  const sidebarRef = useRef(null);
  const [error, setError] = useState({});
  const location = useLocation();
  const currentPath = location.pathname;
  const vocabularyType = extractVariablePart(currentPath);
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");
  // currently we want the app to work in the following ways:
  // 1. Possibility to add a child, which means I am sending h-parent in the request
  // 2. Possibility to just add item which means this is a top level item and I am
  // not sending anything for hierarchy
  // 3. editing an item, which means I need to send parent if the item
  // as it and not send a parent if item does not have it
  const onSubmit = (values, formik) => {
    let preparedValues;

    if (newChildItemParentId) {
      preparedValues = {
        ...values,
        title: transformArrayToObject(values.title),
        type: vocabularyType,
        props: eliminateEmptyStringProperties(values.props),
        hierarchy: { parent: newChildItemParentId },
      };
    } else if (!editMode) {
      preparedValues = {
        ...values,
        title: transformArrayToObject(values.title),
        type: vocabularyType,
        props: eliminateEmptyStringProperties(values.props),
      };
    } else {
      preparedValues = {
        ...values,
        title: transformArrayToObject(values.title),
        type: vocabularyType,
        props: eliminateEmptyStringProperties(values.props),
        hierarchy: record.hierarchy.parent
          ? { parent: record.hierarchy.parent }
          : {},
      };
    }
    if (editMode) {
      http
        .put(apiCallUrl, preparedValues)
        .then((response) => {
          setError({});
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
          setError({});
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
          validationSchema: VocabularyFormSchema,
          validateOnChange: false,
          validateOnBlur: false,
        }}
      >
        <Grid>
          <Grid.Row>
            <Grid.Column width={16}>
              <CurrentLocationInformation
                record={record}
                editMode={editMode}
                newChildItemParentId={newChildItemParentId}
              />
            </Grid.Column>
          </Grid.Row>

          <Grid.Column mobile={16} tablet={16} computer={12}>
            <MultiLingualTextInput fieldPath="title" options={options} />
            <TextField fieldPath="id" label={"ID"} width={11} required />
            {hasPropFields && (
              <PropFieldsComponent vocabularyProps={vocabularyProps} />
            )}
            <FormikStateLogger />
            {error.message && <ErrorComponent error={error} />}
          </Grid.Column>
          <Ref innerRef={sidebarRef}>
            <Grid.Column mobile={16} tablet={16} computer={4}>
              <Sticky context={sidebarRef} offset={20}>
                {/* need to fix bug it expects only one child */}
                <Overridable id="FormApp.buttons">
                  <React.Fragment>
                    <PublishButton />
                    <ResetButton />
                  </React.Fragment>
                </Overridable>
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
    title: PropTypes.arrayOf(TitlePropType),
    ICO: PropTypes.string,
    RID: PropTypes.string,
    acronym: PropTypes.string,
    nameType: PropTypes.string,
  }),
  vocabularyProps: PropTypes.object,
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
