import * as React from "react";
import PropTypes from "prop-types";
import { BaseForm, FormFeedback } from "@js/oarepo_ui";
import { VocabularyFormSchema } from "@js/oarepo_vocabularies";
import { Grid, Ref, Sticky, Modal, Button } from "semantic-ui-react";
import { buildUID } from "react-searchkit";
import Overridable, {
  OverridableContext,
  overrideStore,
} from "react-overridable";
import { CustomFields, http } from "react-invenio-forms";
import { VocabularyFormFields } from "../VocabularyFormFields";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

const SubmitButton = ({ formRef }) => {
  const handleSubmit = () => {
    if (formRef.current) {
      formRef.current.handleSubmit();
    }
  };

  return (
    <Button
      primary
      onClick={() => handleSubmit()}
      type="submit"
      form="vocabulary-form"
    >
      {i18next.t("Submit")}
    </Button>
  );
};

SubmitButton.propTypes = {
  formRef: PropTypes.any,
};

export const VocabularyAddItemForm = ({
  backToSearch,
  onSubmit,
  vocabulary,
  overriddenComponents,
}) => {
  const formFeedbackRef = React.useRef(null);
  const overridableIdPrefix = "Oarepovocabularies.Form";
  const formRef = React.useRef();
  const [customFields, setCustomFields] = React.useState(null);
  React.useEffect(() => {
    const fetchVocabulariesFormConfig = async () => {
      const response = await http.get(
        `/configs/vocabularies/${vocabulary}/form`
      );
      setCustomFields(response.data.custom_fields.ui);
    };
    fetchVocabulariesFormConfig();
  }, [vocabulary]);
  const componentOverrides = React.useMemo(() => {
    return {
      ...overrideStore.getAll(),
      ...overriddenComponents,
    };
  }, [overriddenComponents]);
  return (
    <OverridableContext.Provider value={componentOverrides}>
      <Modal.Content>
        <BaseForm
          id="vocabulary-form"
          onSubmit={onSubmit}
          formik={{
            innerRef: formRef,
            initialValues: { id: "" },
            validateOnChange: false,
            validateOnBlur: true,
            enableReinitialize: true,
            validationSchema: VocabularyFormSchema,
          }}
        >
          <Grid>
            <Ref innerRef={formFeedbackRef}>
              <Grid.Column
                id="main-content"
                mobile={16}
                tablet={16}
                computer={16}
              >
                <Sticky context={formFeedbackRef} offset={20}>
                  <Overridable
                    id={buildUID(overridableIdPrefix, "Errors.container")}
                  >
                    <FormFeedback />
                  </Overridable>
                </Sticky>
                <Overridable
                  id={buildUID(overridableIdPrefix, "FormFields.container")}
                >
                  <VocabularyFormFields />
                </Overridable>
                <Overridable
                  id={buildUID(overridableIdPrefix, "CustomFields.container")}
                >
                  {customFields?.length > 0 && (
                    <CustomFields
                      config={customFields}
                      templateLoaders={[
                        (widget) =>
                          import(`@templates/custom_fields/${widget}.js`),
                        (widget) => import(`react-invenio-forms`),
                      ]}
                    />
                  )}
                </Overridable>
              </Grid.Column>
            </Ref>
          </Grid>
        </BaseForm>
      </Modal.Content>
      <Modal.Actions>
        <Button
          icon="arrow left"
          content={i18next.t("Back to search")}
          onClick={() => backToSearch()}
        />
        <SubmitButton onSubmit={onSubmit} formRef={formRef} />
      </Modal.Actions>
    </OverridableContext.Provider>
  );
};

VocabularyAddItemForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  backToSearch: PropTypes.func,
  overriddenComponents: PropTypes.object,
  vocabulary: PropTypes.string.isRequired,
};

VocabularyAddItemForm.defaultProps = {};

export default VocabularyAddItemForm;
