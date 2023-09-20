import * as Yup from "yup";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import _uniqWith from "lodash/uniqWith";

const checkDuplicateLanguage = (array) => {
  const uniqueArray = _uniqWith(
    array,
    (itemA, itemB) => itemA.language === itemB.language
  );
  return uniqueArray.length === array.length;
};

export const VocabularyFormSchema = Yup.object().shape({
  _title: Yup.array().of(
    Yup.object().shape({
      lang: Yup.string().required(i18next.t("required")),
      name: Yup.string().required(i18next.t("required")),
    })
  ),
  props: Yup.object()
    .shape({
      ICO: Yup.string()
        .length(8, ({ length }) =>
          i18next.t("invalidLengthError", { length: length })
        )
        .matches(/^\d+$/, i18next.t("notANumberError")),
      RID: Yup.string().length(5, ({ length }) =>
        i18next.t("invalidLengthError", { length: length })
      ),
    })
    .nullable(),
  id: Yup.string().required(i18next.t("required")),
});
