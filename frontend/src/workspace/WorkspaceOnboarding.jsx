import WorkspaceForm from "./WorkspaceForm";
import useWorkspace from "./useWorkspace";

function WorkspaceOnboarding() {
  const {
    createWorkspace,
  } = useWorkspace();

  return (
    <section className="workspace-onboarding">
      <div className="workspace-onboarding-heading">
        <span className="eyebrow">
          Business workspace
        </span>

        <h2>
          Create your first workspace
        </h2>

        <p>
          This profile becomes the
          authoritative context for every
          Nestora module.
        </p>
      </div>

      <WorkspaceForm
        submitLabel="Create workspace"
        onSubmit={createWorkspace}
      />
    </section>
  );
}

export default WorkspaceOnboarding;
