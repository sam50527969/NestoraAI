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

import CRMBoard from "../CRMBoard";

vi.mock("../CRMColumn", () => ({
  default: ({
    title,
    leads,
    onSelectLead,
    onStageChange,
    updatingLeadId,
  }) => (
    <section data-testid={`stage-${title}`}>
      <h2>{title}</h2>

      <span>
        {leads.length}
      </span>

      {leads.map((lead) => (
        <div key={lead.id}>
          <span>{lead.name}</span>

          {updatingLeadId ===
            lead.id && (
            <span>Updating</span>
          )}

          <button
            type="button"
            onClick={() =>
              onSelectLead(lead)
            }
          >
            Select {lead.name}
          </button>

          <button
            type="button"
            onClick={() =>
              onStageChange(
                lead,
                "Qualified",
              )
            }
          >
            Move {lead.name}
          </button>
        </div>
      ))}
    </section>
  ),
}));

const leads = [
  {
    id: 1,
    name: "New Clinic",
    status: "New",
  },
  {
    id: 2,
    name: "Contacted Garage",
    status: "Contacted",
  },
  {
    id: 3,
    name: "Qualified Cafe",
    status: "Qualified",
  },
  {
    id: 4,
    name: "Won Restaurant",
    status: "Won",
  },
  {
    id: 5,
    name: "Lost Salon",
    status: "Lost",
  },
  {
    id: 6,
    name: "Default Stage Lead",
  },
];

describe("CRMBoard", () => {
  it("renders every pipeline stage", () => {
    render(
      <CRMBoard
        leads={leads}
        onSelectLead={vi.fn()}
        onStageChange={vi.fn()}
        updatingLeadId={null}
      />,
    );

    for (const stage of [
      "New",
      "Contacted",
      "Qualified",
      "Won",
      "Lost",
    ]) {
      expect(
        screen.getByTestId(
          `stage-${stage}`,
        ),
      ).toBeInTheDocument();
    }
  });

  it("places leads in their correct stages", () => {
    render(
      <CRMBoard
        leads={leads}
        onSelectLead={vi.fn()}
        onStageChange={vi.fn()}
        updatingLeadId={null}
      />,
    );

    const newStage =
      screen.getByTestId(
        "stage-New",
      );

    expect(
      newStage,
    ).toHaveTextContent(
      "New Clinic",
    );

    expect(
      newStage,
    ).toHaveTextContent(
      "Default Stage Lead",
    );

    expect(
      screen.getByTestId(
        "stage-Contacted",
      ),
    ).toHaveTextContent(
      "Contacted Garage",
    );

    expect(
      screen.getByTestId(
        "stage-Qualified",
      ),
    ).toHaveTextContent(
      "Qualified Cafe",
    );
  });

  it("passes selection and stage-change actions through", () => {
    const onSelectLead = vi.fn();
    const onStageChange = vi.fn();

    render(
      <CRMBoard
        leads={leads}
        onSelectLead={onSelectLead}
        onStageChange={onStageChange}
        updatingLeadId={2}
      />,
    );

    fireEvent.click(
      screen.getByRole(
        "button",
        {
          name:
            "Select Contacted Garage",
        },
      ),
    );

    expect(
      onSelectLead,
    ).toHaveBeenCalledWith(
      leads[1],
    );

    fireEvent.click(
      screen.getByRole(
        "button",
        {
          name:
            "Move Contacted Garage",
        },
      ),
    );

    expect(
      onStageChange,
    ).toHaveBeenCalledWith(
      leads[1],
      "Qualified",
    );

    expect(
      screen.getByTestId(
        "stage-Contacted",
      ),
    ).toHaveTextContent(
      "Updating",
    );
  });
});