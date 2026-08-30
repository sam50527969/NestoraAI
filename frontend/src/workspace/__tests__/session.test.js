import {
  afterEach,
  describe,
  expect,
  it,
} from "vitest";

import {
  clearActiveBusinessUid,
  getActiveBusinessUid,
  setActiveBusinessUid,
} from "../session";

afterEach(() => {
  window.sessionStorage.clear();
});

describe("active workspace session", () => {
  it("stores and reads the active business UID", () => {
    setActiveBusinessUid("biz_active");

    expect(
      getActiveBusinessUid(),
    ).toBe("biz_active");
  });

  it("clears blank and explicit values", () => {
    setActiveBusinessUid("biz_active");
    setActiveBusinessUid("   ");

    expect(
      getActiveBusinessUid(),
    ).toBeNull();

    setActiveBusinessUid("biz_active");
    clearActiveBusinessUid();

    expect(
      getActiveBusinessUid(),
    ).toBeNull();
  });
});
