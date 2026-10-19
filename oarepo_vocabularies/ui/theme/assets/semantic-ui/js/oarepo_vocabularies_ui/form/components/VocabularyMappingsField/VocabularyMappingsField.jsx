// SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

import React from "react";
import { ArrayField, SelectField, TextField } from "react-invenio-forms";
import { ArrayFieldItem } from "@js/oarepo_ui/forms";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

// SKOS mapping relations accepted by the backend (SKOSMappingSchema)
const skosRelationOptions = [
  { key: "exactMatch", value: "exactMatch", text: i18next.t("Exact match") },
  { key: "closeMatch", value: "closeMatch", text: i18next.t("Close match") },
  { key: "broadMatch", value: "broadMatch", text: i18next.t("Broad match") },
  { key: "narrowMatch", value: "narrowMatch", text: i18next.t("Narrow match") },
  {
    key: "relatedMatch",
    value: "relatedMatch",
    text: i18next.t("Related match"),
  },
];

export const VocabularyMappingsField = () => (
  <ArrayField
    fieldPath="mappings"
    label={i18next.t("Mappings")}
    labelIcon="linkify"
    helpText={i18next.t(
      "Concepts in external vocabularies (e.g. COAR) that this item corresponds to, with the kind of SKOS relation."
    )}
    addButtonLabel={i18next.t("Add mapping")}
    defaultNewValue={{ relation: "", scheme: "", identifier: "" }}
  >
    {({ arrayHelpers, indexPath }) => {
      const fieldPathPrefix = `mappings.${indexPath}`;
      return (
        <ArrayFieldItem
          indexPath={indexPath}
          arrayHelpers={arrayHelpers}
          fieldPathPrefix={fieldPathPrefix}
        >
          <SelectField
            width={4}
            fieldPath={`${fieldPathPrefix}.relation`}
            label={i18next.t("Relation")}
            options={skosRelationOptions}
            selectOnBlur={false}
            required
          />
          <TextField
            width={5}
            fieldPath={`${fieldPathPrefix}.scheme`}
            label={i18next.t("Scheme")}
            placeholder="http://purl.org/coar/resource_type/"
            required
          />
          <TextField
            width={7}
            fieldPath={`${fieldPathPrefix}.identifier`}
            label={i18next.t("Identifier")}
            placeholder="http://purl.org/coar/resource_type/c_ddb1"
            required
          />
        </ArrayFieldItem>
      );
    }}
  </ArrayField>
);
