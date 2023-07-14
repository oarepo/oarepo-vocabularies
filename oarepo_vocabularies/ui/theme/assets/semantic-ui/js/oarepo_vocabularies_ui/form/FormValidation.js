import * as Yup from "yup";
import { checkDuplicateLanguage } from "../utils";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

export const MyFormSchema = Yup.object().shape({
  title: Yup.array()
    .of(
      Yup.object().shape({
        language: Yup.string().required(i18next.t("required")),
        title: Yup.string().required(i18next.t("required")),
      })
    )
    .test(
      "same language",
      (value) => {
        return [
          value.value.map((item) => ({
            language: i18next.t("languageError"),
          })),
        ];
      },
      (value, context) => {
        return checkDuplicateLanguage(value);
      }
    ),
  props: Yup.object().shape({
    ICO: Yup.string()
      .length(8, ({ length }) => i18next.t("lengthError", { length: length }))
      .matches(/^\d+$/, i18next.t("numbersError")),
    RID: Yup.string().length(5, ({ length }) =>
      i18next.t("lengthError", { length: length })
    ),
  }),
  id: Yup.string().required(i18next.t("required")),
});
