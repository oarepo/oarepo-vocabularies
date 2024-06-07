import * as Yup from "yup";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";
import { invalidUrlMessage } from "@js/oarepo_ui";

export const VocabularyFormSchema = Yup.object().shape({
  _title: Yup.array().of(
    Yup.object().shape({
      lang: Yup.string().required(i18next.t("required")),
      name: Yup.string().required(i18next.t("required")),
    })
  ),
  icon: Yup.string().url(invalidUrlMessage),
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
