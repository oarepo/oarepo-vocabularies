import React from "react";
import { Container, Grid, Ref, Sticky } from "semantic-ui-react";
import { useFormConfig, FormFeedback, FormTitle } from "@js/oarepo_ui/forms";
import { useLocation } from "react-router-dom";
import _has from "lodash/has";
import Overridable from "react-overridable";
import { buildUID } from "react-searchkit";
import {
  VocabularyFormControlPanel,
  VocabularyFormFields,
  CurrentLocationInformation,
} from "./components";
import { CustomFields } from "react-invenio-forms";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { DepositBootstrap } from "@js/invenio_rdm_records/src/deposit/api/DepositBootstrap";

export const FormAppLayout = () => {
  const { config } = useFormConfig();

  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const newChildItemParentId = searchParams.get("h-parent");
  const isUpdateForm = _has(config, "updateUrl");

  return (
    <Container fluid>
      <Grid>
        <Grid.Row className="rel-mb-2">
          <Grid.Column width={16}>
            <CurrentLocationInformation
              isUpdateForm={isUpdateForm}
              newChildItemParentId={newChildItemParentId}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>

      <BaseFormLayout />
    </Container>
  );
};
export default FormAppLayout;

const BaseFormLayoutComponent = ({ formikProps = {}, record, errors = {} }) => {
  const {
    config: { overridableIdPrefix, custom_fields: customFields },
  } = useFormConfig();
  const sidebarRef = React.useRef(null);
  const formFeedbackRef = React.useRef(null);

  return (
    <DepositBootstrap>
      <Grid>
        <Ref innerRef={formFeedbackRef}>
          <Grid.Column id="main-content" mobile={16} tablet={16} computer={11}>
            {/* <FormTitle /> */}
            <Sticky context={formFeedbackRef} offset={20}>
              <Overridable
                id={buildUID(overridableIdPrefix, "Errors.container")}
              >
                <FormFeedback />
              </Overridable>
            </Sticky>
            <Overridable
              id={buildUID(overridableIdPrefix, "FormFields.container")}
              record={record}
            >
              <VocabularyFormFields />
            </Overridable>
            <Overridable
              id={buildUID(overridableIdPrefix, "CustomFields.container")}
            >
              <CustomFields
                config={customFields?.ui}
                templateLoaders={[
                  (widget) => import(`@templates/custom_fields/${widget}.js`),
                  (widget) => import(`react-invenio-forms`),
                ]}
              />
            </Overridable>
          </Grid.Column>
        </Ref>
        <Ref innerRef={sidebarRef}>
          <Grid.Column id="control-panel" mobile={16} tablet={16} computer={5}>
            <Overridable
              id={buildUID(overridableIdPrefix, "FormActions.container")}
              record={record}
            >
              <VocabularyFormControlPanel />
            </Overridable>
          </Grid.Column>
        </Ref>
      </Grid>
    </DepositBootstrap>
  );
};

const mapStateToProps = (state) => {
  return {
    record: state.deposit.record,
    errors: state.deposit.errors,
  };
};

export const BaseFormLayout = connect(
  mapStateToProps,
  null
)(BaseFormLayoutComponent);

BaseFormLayoutComponent.propTypes = {
  record: PropTypes.object.isRequired,
  // eslint-disable-next-line react/require-default-props
  errors: PropTypes.object,
  // eslint-disable-next-line react/require-default-props
  formikProps: PropTypes.object,
};
