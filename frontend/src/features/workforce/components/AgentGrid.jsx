import AgentCard from "./AgentCard";

const DEFAULT_AGENTS = [
  {
    name: "CEO Agent",
    role: "Mission planning",
    icon: "🧠",
    status: "completed",
    progress: 100,
    currentTask: "Mission planned",
  },
  {
    name: "Research Agent",
    role: "Finding businesses",
    icon: "🔍",
    status: "running",
    progress: 72,
    currentTask: "Searching restaurants in Doha",
  },
  {
    name: "Website Agent",
    role: "Website analysis",
    icon: "🌐",
    status: "running",
    progress: 38,
    currentTask: "Checking websites",
  },
  {
    name: "Sales Agent",
    role: "Lead scoring",
    icon: "📈",
    status: "waiting",
    progress: 0,
    currentTask: "Waiting for research",
  },
  {
    name: "Proposal Agent",
    role: "Proposal generation",
    icon: "📝",
    status: "waiting",
    progress: 0,
    currentTask: "Awaiting analysis",
  },
  {
    name: "CRM Agent",
    role: "Saving leads",
    icon: "💾",
    status: "waiting",
    progress: 0,
    currentTask: "Waiting for AI",
  },
];

export default function AgentGrid({
  agents = DEFAULT_AGENTS,
}) {
  return (
    <section className="workforce-grid">
      {agents.map((agent) => (
        <AgentCard
          key={agent.name}
          {...agent}
        />
      ))}
    </section>
  );
}