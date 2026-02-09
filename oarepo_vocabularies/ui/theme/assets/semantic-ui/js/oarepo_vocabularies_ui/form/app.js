import FormAppLayout from "./FormAppLayout";
import {
  VocabularyFormFieldsAwards,
  VocabularyFormFieldsNames,
  VocabularyFormFieldsFunders,
  VocabularyFormFieldsAffiliations,
} from "./components";
import { DepositFormApp, parseFormAppConfig } from "@js/oarepo_ui/forms";
import React from "react";
import { RDMDepositRecordSerializer } from "@js/invenio_rdm_records/src/deposit/api/DepositRecordSerializer";
import { Field } from "@js/invenio_rdm_records/src/deposit/serializers";
import ReactDOM from "react-dom";
import _get from "lodash/get";
import _set from "lodash/set";
import _cloneDeep from "lodash/cloneDeep";

export class I18nField extends Field {
  constructor({ fieldpath, deserializedDefault = [], serializedDefault = {} }) {
    super({ fieldpath, deserializedDefault, serializedDefault });
  }

  deserialize(record) {
    const recordClone = _cloneDeep(record);
    const rawValue = _get(
      recordClone,
      this.fieldpath,
      this.deserializedDefault
    );
    if (!rawValue || typeof rawValue !== "object" || Array.isArray(rawValue)) {
      return _set(recordClone, this.fieldpath, this.deserializedDefault);
    }

    const arrayValue = Object.entries(rawValue).map(([lang, value]) => ({
      lang,
      value,
    }));

    return _set(recordClone, this.fieldpath, arrayValue);
  }

  serialize(record) {
    const recordClone = _cloneDeep(record);
    const arrayValue = _get(
      recordClone,
      this.fieldpath,
      this.serializedDefault
    );

    if (!Array.isArray(arrayValue)) {
      return _set(recordClone, this.fieldpath, this.serializedDefault);
    }

    const objValue = {};
    for (const { lang, value } of arrayValue) {
      if (lang && value !== undefined && value !== null) {
        objValue[lang] = value;
      }
    }

    return _set(recordClone, this.fieldpath, objValue);
  }
}

// necessary because RDM serializer manipulates some fields that don't exist in
// vocabulary records
class VocabularyRecordSerializer extends RDMDepositRecordSerializer {
  get depositRecordSchema() {
    return {
      title: new I18nField({ fieldpath: "title" }),
    };
  }
  deserialize(record) {
    let deserializedRecord = this._removeEmptyValues(record);
    for (const key in this.depositRecordSchema) {
      deserializedRecord = this.depositRecordSchema[key].deserialize(
        deserializedRecord,
        this.defaultLocale
      );
    }
    return deserializedRecord;
  }

  serialize(record) {
    let serializedRecord = this._removeEmptyValues(record);
    for (const key in this.depositRecordSchema) {
      serializedRecord = this.depositRecordSchema[key].serialize(
        serializedRecord,
        this.defaultLocale
      );
    }
    return serializedRecord;
  }
}

const { rootEl, config, ...rest } = parseFormAppConfig();
const { overridableIdPrefix } = config;
const vocabularyRecordSerializer = new VocabularyRecordSerializer(
  config.default_locale,
  config.custom_fields.vocabularies
);
export const componentOverrides = {
  [`${overridableIdPrefix}.FormApp.layout`]: FormAppLayout,
  [`${overridableIdPrefix}.FormFields.container.awards`]:
    VocabularyFormFieldsAwards,
  [`${overridableIdPrefix}.FormFields.container.names`]:
    VocabularyFormFieldsNames,
  [`${overridableIdPrefix}.FormFields.container.funders`]:
    VocabularyFormFieldsFunders,
  [`${overridableIdPrefix}.FormFields.container.affiliations`]:
    VocabularyFormFieldsAffiliations,
};

ReactDOM.render(
  <DepositFormApp
    config={config}
    {...rest}
    recordSerializer={vocabularyRecordSerializer}
    componentOverrides={componentOverrides}
  />,
  rootEl
);
