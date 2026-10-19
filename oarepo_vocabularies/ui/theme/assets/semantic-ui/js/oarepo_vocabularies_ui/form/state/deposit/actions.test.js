// SPDX-FileCopyrightText: 2026 CESNET z.s.p.o.
// SPDX-License-Identifier: MIT

import { DRAFT_SAVE_FAILED } from "@js/invenio_rdm_records/src/deposit/state/types";
import { SET_VALIDATION_ERRORS } from "@js/oarepo_ui/forms/state/deposit/types";
import { createOrUpdate } from "./actions";

const saveFailingWith = async (errors) => {
  const dispatch = jest.fn();
  const config = {
    config: { createUrl: "/api/vocabularies/languages" },
    service: { drafts: { create: jest.fn().mockRejectedValue({ errors }) } },
  };
  jest.spyOn(console, "error").mockImplementation(() => {});
  await expect(
    createOrUpdate({ id: "eng" }, {})(dispatch, jest.fn(), config)
  ).rejects.toEqual({ errors });
  return dispatch.mock.calls.map(([action]) => action).at(-1);
};

describe("createOrUpdate", () => {
  it("shows field errors next to the inputs on a validation error", async () => {
    const fieldErrors = { mappings: [{ relation: ["Missing data."] }] };
    const action = await saveFailingWith(fieldErrors);
    expect(action.type).toBe(SET_VALIDATION_ERRORS);
    expect(action.payload.errors).toEqual(fieldErrors);
  });

  it("reports any other failure as a failed save", async () => {
    const action = await saveFailingWith({ status: 403, message: "Denied" });
    expect(action.type).toBe(DRAFT_SAVE_FAILED);
    expect(action.payload.formFeedbackMessage).toBe("Denied");
  });
});
