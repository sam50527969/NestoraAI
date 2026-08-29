import {
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";

import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  getCEOExecution,
  getCEOExecutions,
} from "../../../../api";

import CEOExecutionHistory from "../CEOExecutionHistory";


vi.mock("../../../../api", () => ({
  getCEOExecution: vi.fn(),
  getCEOExecutions: vi.fn(),
}));


const executions = [
  {
    execution_uid: "exec_success_001",
    approval_uid: "approval_001",
    mission_id: "mission_001",
    workflow_id: "workflow_001",
    objective: "Contact priority leads",
    status: "completed",
    success: true,
    completed_task_count: 3,
    failed_task_count: 0,
    error: null,
    completed_at: "2026-08-29T08:00:00",
    created_at: "2026-08-29T07:55:00",
  },
  {
    execution_uid: "exec_failed_002",
    approval_uid: "approval_002",
    mission_id: null,
    workflow_id: null,
    objective: "Generate executive proposal",
    status: "failed",
    success: false,
    completed_task_count: 1,
    failed_task_count: 1,
    error: "Proposal generation failed.",
    completed_at: "2026-08-29T09:00:00",
    created_at: "2026-08-29T08:55:00",
  },
];


describe("CEOExecutionHistory", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    getCEOExecutions.mockResolvedValue({
      executions,
      count: 2,
      limit: 20,
      offset: 0,
    });
  });


  it("loads and renders execution history", async () => {
    render(
      <CEOExecutionHistory />,
    );

    expect(
      screen.getByText(
        "Loading execution history...",
      ),
    ).toBeInTheDocument();

    expect(
      await screen.findByText(
        "Contact priority leads",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Generate executive proposal",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "1 Successful",
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "1 Failed",
      ),
    ).toBeInTheDocument();

    expect(
      getCEOExecutions,
    ).toHaveBeenCalledWith({
      limit: 20,
      offset: 0,
    });
  });


  it("loads persistent execution details", async () => {
    getCEOExecution.mockResolvedValue({
      ...executions[0],
      result: {
        message:
          "Priority outreach completed.",
        outreach_packages: [],
      },
    });

    render(
      <CEOExecutionHistory />,
    );

    await screen.findByText(
      "Contact priority leads",
    );

    const detailButtons =
      screen.getAllByRole(
        "button",
        {
          name: "View Details",
        },
      );

    fireEvent.click(
      detailButtons[0],
    );

    await waitFor(() => {
      expect(
        getCEOExecution,
      ).toHaveBeenCalledWith(
        "exec_success_001",
      );
    });

    expect(
      await screen.findByText(
        /Priority outreach completed/,
      ),
    ).toBeInTheDocument();

    expect(
      screen.getByRole(
        "button",
        {
          name: "Hide Details",
        },
      ),
    ).toBeInTheDocument();
  });


  it("renders execution errors", async () => {
    render(
      <CEOExecutionHistory />,
    );

    expect(
      await screen.findByText(
        "Proposal generation failed.",
      ),
    ).toBeInTheDocument();
  });


  it("renders the empty state", async () => {
    getCEOExecutions.mockResolvedValue({
      executions: [],
      count: 0,
      limit: 20,
      offset: 0,
    });

    render(
      <CEOExecutionHistory />,
    );

    expect(
      await screen.findByText(
        "No CEO executions have been recorded yet.",
      ),
    ).toBeInTheDocument();
  });


  it("renders API failures", async () => {
    getCEOExecutions.mockRejectedValue(
      new Error(
        "Execution history unavailable.",
      ),
    );

    render(
      <CEOExecutionHistory />,
    );

    expect(
      await screen.findByText(
        "Execution history unavailable.",
      ),
    ).toBeInTheDocument();
  });
});
