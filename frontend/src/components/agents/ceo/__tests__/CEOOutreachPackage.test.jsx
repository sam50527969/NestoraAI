import {
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import CEOOutreachPackage from "../CEOOutreachPackage";

const preparedOutreach = {
  activity_uid: "activity-123",
  lead_name: "Test Lead",
  status: "prepared",
  email_subject: "Test subject",
  email_body: "Test email body",
};

function renderPackage(overrides = {}) {
  const onMarkSent = vi.fn();
  const onSendEmail = vi.fn();

  render(
    <CEOOutreachPackage
      outreach={{
        ...preparedOutreach,
        ...overrides,
      }}
      onMarkSent={onMarkSent}
      onSendEmail={onSendEmail}
    />,
  );

  fireEvent.click(
    screen.getByRole("button", {
      name: /test lead/i,
    }),
  );

  return {
    onMarkSent,
    onSendEmail,
  };
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("CEOOutreachPackage email delivery", () => {
  it("does not send when confirmation is cancelled", () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);

    const { onSendEmail } = renderPackage();

    fireEvent.click(
      screen.getByRole("button", {
        name: "Send Email",
      }),
    );

    expect(window.confirm).toHaveBeenCalledOnce();
    expect(onSendEmail).not.toHaveBeenCalled();
  });

  it("sends exactly once when confirmation is accepted", () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);

    const { onSendEmail } = renderPackage();

    fireEvent.click(
      screen.getByRole("button", {
        name: "Send Email",
      }),
    );

    expect(window.confirm).toHaveBeenCalledOnce();
    expect(onSendEmail).toHaveBeenCalledOnce();
    expect(onSendEmail).toHaveBeenCalledWith(
      expect.objectContaining({
        activity_uid: "activity-123",
        lead_name: "Test Lead",
      }),
    );
  });

  it("does not offer Send Email for sent outreach", () => {
    renderPackage({
      status: "sent",
    });

    expect(
      screen.queryByRole("button", {
        name: "Send Email",
      }),
    ).not.toBeInTheDocument();
  });

  it("does not offer Send Email without email content", () => {
    renderPackage({
      email_subject: null,
      email_body: null,
    });

    expect(
      screen.queryByRole("button", {
        name: "Send Email",
      }),
    ).not.toBeInTheDocument();
  });
});
