// SPDX-FileCopyrightText: 2023-2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

import React from "react";
import { useFormikContext, connect } from "formik";
import { Button, Container } from "semantic-ui-react";
import { i18next } from "@translations/oarepo_vocabularies_ui/i18next";

const ResetButtonComponent = () => {
  const { handleReset } = useFormikContext();
  return (
    <Container className="mt-5" textAlign="center">
      <Button
        fluid
        color="red"
        onClick={handleReset}
        content={i18next.t("reset")}
        icon="undo"
        labelPosition="left"
        type="reset"
      />
    </Container>
  );
};

export const ResetButton = connect(ResetButtonComponent);
