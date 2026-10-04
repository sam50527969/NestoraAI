import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import ExecutiveBrief from "../ExecutiveBrief";
import AgentStatus from "../AgentStatus";
import ExecutiveHero from "../../../features/dashboard/components/ExecutiveHero";

afterEach(cleanup);

describe("dashboard evidence", () => {
  it("shows only supplied workspace summary rather than a fictional opportunity", () => {
    render(<ExecutiveBrief currency="QAR" pipelineValue={0}
      brief={["You currently have 0 total leads in your CRM."]} />);
    expect(screen.getByText("You currently have 0 total leads in your CRM.")).toBeTruthy();
    expect(screen.queryByText(/AI Shami Home/)).toBeNull();
    expect(screen.queryByText(/High AI score/)).toBeNull();
  });
  it("removes old workspace statements when new workspace evidence arrives", () => {
    const { rerender } = render(<ExecutiveBrief brief={["Workspace A has 4 leads."]} />);
    rerender(<ExecutiveBrief brief={["Workspace B has 0 leads."]} />);
    expect(screen.queryByText("Workspace A has 4 leads.")).toBeNull();
    expect(screen.getByText("Workspace B has 0 leads.")).toBeTruthy();
  });
  it("does not manufacture workforce agents when no live data is supplied", () => {
    render(<AgentStatus />);
    expect(screen.getByText("No executives available")).toBeTruthy();
    expect(screen.queryByText("CEO Agent")).toBeNull();
    expect(screen.queryByText("7")).toBeNull();
  });
  it("does not claim AI opportunities or greet every account as the owner", () => {
    render(<ExecutiveHero />);
    expect(screen.queryByText(/Sam/)).toBeNull();
    expect(screen.queryByText(/identified today's/)).toBeNull();
    expect(screen.getByText("Review your workspace CRM, priorities, and mission progress.")).toBeTruthy();
  });
});
