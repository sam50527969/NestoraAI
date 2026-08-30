import WorkspaceOnboarding from "./WorkspaceOnboarding";
import useWorkspace from "./useWorkspace";

function WorkspaceBoundary({
  children,
}) {
  const {
    isLoading,
    error,
    hasWorkspaces,
    refreshWorkspaces,
  } = useWorkspace();

  if (isLoading) {
    return (
      <section className="workspace-state">
        <div className="workspace-state-content">
          <span className="eyebrow">
            Business workspace
          </span>

          <h2>
            Loading your workspace...
          </h2>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="workspace-state">
        <div className="workspace-state-content">
          <span className="eyebrow">
            Business workspace
          </span>

          <h2>
            We could not load your workspace
          </h2>

          <p>
            Check the backend connection and
            try again.
          </p>

          <button
            type="button"
            className="secondary"
            onClick={refreshWorkspaces}
          >
            Try again
          </button>
        </div>
      </section>
    );
  }

  if (!hasWorkspaces) {
    return <WorkspaceOnboarding />;
  }

  return children;
}

export default WorkspaceBoundary;
