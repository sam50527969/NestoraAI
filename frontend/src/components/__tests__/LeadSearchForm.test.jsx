import {
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import {
  describe,
  expect,
  it,
  vi,
} from "vitest";

import LeadSearchForm from "../LeadSearchForm";

describe("LeadSearchForm", () => {
  it("does not search without a business type", () => {
    const onSearch = vi.fn();

    render(
      <LeadSearchForm onSearch={onSearch} />
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Find Leads",
      })
    );

    expect(onSearch).not.toHaveBeenCalled();

    expect(
      screen.getByRole("alert")
    ).toHaveTextContent(
      "Please enter a business type."
    );
  });

  it("does not search without a location", () => {
    const onSearch = vi.fn();

    render(
      <LeadSearchForm onSearch={onSearch} />
    );

    fireEvent.change(
      screen.getByPlaceholderText(
        "Business type, e.g. Coffee Shop"
      ),
      {
        target: {
          value: "Auto Repair",
        },
      }
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Find Leads",
      })
    );

    expect(onSearch).not.toHaveBeenCalled();

    expect(
      screen.getByRole("alert")
    ).toHaveTextContent(
      "Please enter a location."
    );
  });

  it("submits trimmed valid search data", () => {
    const onSearch = vi.fn();

    render(
      <LeadSearchForm onSearch={onSearch} />
    );

    fireEvent.change(
      screen.getByPlaceholderText(
        "Business type, e.g. Coffee Shop"
      ),
      {
        target: {
          value: "  Auto Repair  ",
        },
      }
    );

    fireEvent.change(
      screen.getByPlaceholderText(
        "Location, e.g. Doha"
      ),
      {
        target: {
          value: "  Dubai  ",
        },
      }
    );

    fireEvent.change(
      screen.getByPlaceholderText(
        "Number of leads, e.g. 50"
      ),
      {
        target: {
          value: "5",
        },
      }
    );

    fireEvent.click(
      screen.getByRole("button", {
        name: "Find Leads",
      })
    );

    expect(onSearch).toHaveBeenCalledTimes(1);

    expect(onSearch).toHaveBeenCalledWith({
      businessType: "Auto Repair",
      location: "Dubai",
      quantity: "5",
    });

    expect(
      screen.queryByRole("alert")
    ).not.toBeInTheDocument();
  });
});
