import * as Yup from "yup";
import { checkDuplicateLanguage } from "./utils";

export const MyFormSchema = Yup.object().shape({
  title: Yup.array()
    .of(
      Yup.object().shape({
        language: Yup.string().required("required"),
        title: Yup.string().required("required"),
      })
    )
    .test(
      "same language",
      (value) => {
        console.log(value.value);
        return [
          value.value.map((item) => ({
            language: "You must not have two same languages",
          })),
        ];
      },
      (value, context) => {
        return checkDuplicateLanguage(value);
      }
    ),

  props: Yup.object().shape({
    ICO: Yup.string()
      .length(8, "Must be exactly 8 characters")
      .matches(/^\d+$/, "Must contain only numbers"),
    RID: Yup.string().length(5),
  }),
  id: Yup.string().required("required"),
});
