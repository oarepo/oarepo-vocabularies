import React from "react";
import { SelectField } from "react-invenio-forms";
import { useFormConfig } from "@js/oarepo_ui";
import { serializeVocabularyItem } from "@js/oarepo_vocabularies";
import { useFormikContext, getIn } from "formik";
import PropTypes from "prop-types";
import { Dropdown, Divider } from "semantic-ui-react";
import _sortBy from "lodash/sortBy";

export const deserializeLocalVocabularyItem = (item) => {
  return Array.isArray(item)
    ? item.map((item) => deserializeLocalVocabularyItem(item))
    : item.id;
};

const InnerDropdown = ({ options, featured, ...rest }) => {
  const featuredValues = featured.map((f) => f.value);
  const otherOptions = options.filter((o) => !featuredValues.includes(o.value));

  return (
    <Dropdown
      options={[
        ...(featured.length
          ? [
              ...featured.sort((a, b) => a.text.localeCompare(b.text)),
              {
                content: <Divider fitted />,
                disabled: true,
                key: "featured-divider",
              },
            ]
          : []),
        ...otherOptions,
      ]}
      {...rest}
    /> 
  );
};

export const LocalVocabularySelectField = ({
  fieldPath,
  multiple,
  optionsListName,
  helpText,
  ...uiProps
}) => {
  const {
    formConfig: { vocabularies },
  } = useFormConfig();

  const { all: allOptions, featured: featuredOptions } =
    vocabularies[optionsListName];

  if (!allOptions) {
    console.error(
      `Do not have options for ${optionsListName} inside:`,
      vocabularies
    );
  }

  const { values, setFieldTouched } = useFormikContext();
  const value = deserializeLocalVocabularyItem(
    getIn(values, fieldPath, multiple ? [] : {})
  );
  return (
    <React.Fragment>
      <SelectField
        // formik exhibits strange behavior when you enable search prop to semantic ui's dropdown i.e. handleBlur stops working - did not investigate the details very deep
        // but imperatively calling setFieldTouched gets the job done
        onBlur={() => setFieldTouched(fieldPath)}
        deburr
        search
        control={InnerDropdown}
        fieldPath={fieldPath}
        multiple={multiple}
        featured={featuredOptions}
        options={allOptions}
        onChange={({ e, data, formikProps }) => {
          formikProps.form.setFieldValue(
            fieldPath,
            serializeVocabularyItem(data.value)
          );
        }}
        value={value}
        {...uiProps}
      />
      <label className="helptext">{helpText}</label>
    </React.Fragment>
  );
};

LocalVocabularySelectField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  multiple: PropTypes.bool,
  optionsListName: PropTypes.string.isRequired,
  helpText: PropTypes.string,
};
