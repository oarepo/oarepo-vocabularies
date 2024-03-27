import React, { useMemo } from "react";
import { SelectField } from "react-invenio-forms";
import { useFormConfig } from "@js/oarepo_ui";
import { useFormikContext, getIn } from "formik";
import PropTypes from "prop-types";
import { Dropdown, Divider, Breadcrumb } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { search } from "@js/oarepo_vocabularies";

export const serializeVocabularyItems = (vocabularyItems) =>
  vocabularyItems.map((vocabularyItem) => {
    const {
      hierarchy: { title: titlesArray },
      text,
    } = vocabularyItem;
    const sections = [
      ...titlesArray.map((title, index) => {
        if (index === 0) {
          return {
            content: <span>{title}</span>,
            key: crypto.randomUUID(),
          };
        } else {
          return {
            content: (
              <span className="ui breadcrumb vocabulary-parent-item">
                {title}
              </span>
            ),
            key: crypto.randomUUID(),
          };
        }
      }),
    ];
    return {
      ...vocabularyItem,
      text:
        titlesArray.length === 1 ? (
          <span>{text}</span>
        ) : (
          <Breadcrumb icon="left angle" sections={sections} />
        ),
      name: text,
    };
  });

export const processVocabularyItems = (
  options,
  showLeafsOnly,
  filterFunction
) => {
  let serlializedOptions = serializeVocabularyItems(options);
  if (showLeafsOnly) {
    serlializedOptions = serlializedOptions.filter(
      (o) => o.element_type === "leaf"
    );
  }
  if (filterFunction) {
    serlializedOptions = filterFunction(serlializedOptions);
  }
  return serlializedOptions;
};

const InnerDropdown = ({
  options,
  featured,
  usedOptions = [],
  value,
  ...rest
}) => {
  const _filterUsed = (opts) =>
    opts.filter((o) => !usedOptions.includes(o.value) || o.value === value);
  const allOptions = _filterUsed([
    ...(featured.length
      ? [
          ...featured.sort((a, b) => a.name.localeCompare(b.name)),
          {
            content: <Divider fitted />,
            disabled: true,
            key: "featured-divider",
          },
        ]
      : []),
    ...options.filter((o) => !featured.map((o) => o.value).includes(o.value)),
  ]);

  return (
    <Dropdown search={search} options={allOptions} value={value} {...rest} />
  );
};

InnerDropdown.propTypes = {
  options: PropTypes.array.isRequired,
  featured: PropTypes.array,
  usedOptions: PropTypes.array,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string),
  ]),
};
export const LocalVocabularySelectField = ({
  fieldPath,
  multiple,
  optionsListName,
  usedOptions = [],
  helpText,
  showLeafsOnly,
  optimized,
  filterFunction,
  ...uiProps
}) => {
  const {
    formConfig: { vocabularies },
  } = useFormConfig();

  if (!vocabularies) {
    console.error("Do not have vocabularies in formConfig");
  }

  if (!vocabularies[optionsListName]) {
    console.error(
      "Vocabulary with name ",
      optionsListName,
      " not found in formConfig"
    );
  }

  const { all: allOptions, featured: featuredOptions } =
    vocabularies[optionsListName];

  if (!allOptions) {
    console.error(
      `Do not have options for ${optionsListName} inside:`,
      vocabularies
    );
  }

  let serializedOptions = useMemo(
    () => processVocabularyItems(allOptions, showLeafsOnly, filterFunction),
    [allOptions, showLeafsOnly, filterFunction]
  );

  let serializedFeaturedOptions = useMemo(
    () =>
      processVocabularyItems(featuredOptions, showLeafsOnly, filterFunction),
    [featuredOptions, showLeafsOnly, filterFunction]
  );

  const handleChange = ({ e, data, formikProps }) => {
    if (multiple) {
      let vocabularyItems = allOptions.filter((o) =>
        data.value.includes(o.value)
      );
      vocabularyItems = vocabularyItems.map((vocabularyItem) => {
        return { ...vocabularyItem, id: vocabularyItem.value };
      });
      formikProps.form.setFieldValue(fieldPath, [...vocabularyItems]);
    } else {
      let vocabularyItem = allOptions.find((o) => o.value === data.value);
      vocabularyItem = { ...vocabularyItem, id: vocabularyItem?.value };
      formikProps.form.setFieldValue(fieldPath, vocabularyItem);
    }
  };

  const { values, setFieldTouched } = useFormikContext();
  const value = getIn(values, fieldPath, multiple ? [] : {});

  return (
    <React.Fragment>
      <SelectField
        selectOnBlur={false}
        optimized={optimized}
        onBlur={() => setFieldTouched(fieldPath)}
        deburr
        search={search}
        control={InnerDropdown}
        fieldPath={fieldPath}
        multiple={multiple}
        featured={serializedFeaturedOptions}
        options={serializedOptions}
        usedOptions={usedOptions}
        onChange={handleChange}
        value={multiple ? value.map((o) => o?.id) : value?.id}
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
  noResultsMessage: PropTypes.string,
  usedOptions: PropTypes.array,
  showLeafsOnly: PropTypes.bool,
  optimized: PropTypes.bool,
  filterFunction: PropTypes.func,
};

LocalVocabularySelectField.defaultProps = {
  noResultsMessage: i18next.t("No results found."),
  showLeafsOnly: false,
  optimized: false,
  filterFunction: undefined,
};
