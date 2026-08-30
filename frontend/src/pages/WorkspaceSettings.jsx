import {
  useState,
} from "react";

import WorkspaceForm from "../workspace/WorkspaceForm";
import useWorkspace from "../workspace/useWorkspace";

function WorkspaceSettings() {
  const {
    activeWorkspace,
    createWorkspace,
    updateWorkspace,
  } = useWorkspace();

  const [
    showCreate,
    setShowCreate,
  ] = useState(false);

  const [
    saved,
    setSaved,
  ] = useState("");

  async function saveActive(
    payload,
  ) {
    await updateWorkspace(
      activeWorkspace.business_uid,
      payload,
    );

    setSaved(
      "Workspace settings saved.",
    );
  }

  async function createAdditional(
    payload,
  ) {
    await createWorkspace(payload);
    setShowCreate(false);
    setSaved(
      "Workspace created and selected.",
    );
  }

  return (
    <section className="workspace-settings-page">
      <header className="workspace-settings-header">
        <div>
          <span className="eyebrow">
            Workspace settings
          </span>

          <h2>
            {activeWorkspace.name}
          </h2>

          <p>
            Manage the authoritative
            business context used by
            Nestora modules.
          </p>
        </div>

        <button
          type="button"
          className="secondary"
          onClick={() => {
            setShowCreate(
              (current) => !current,
            );
            setSaved("");
          }}
        >
          {showCreate
            ? "Close new workspace"
            : "Add workspace"}
        </button>
      </header>

      {saved && (
        <div
          className="workspace-form-success"
          role="status"
        >
          {saved}
        </div>
      )}

      {showCreate ? (
        <div className="workspace-create-panel">
          <h3>Create another workspace</h3>

          <WorkspaceForm
            submitLabel="Create and select"
            onSubmit={createAdditional}
            onCancel={() =>
              setShowCreate(false)
            }
          />
        </div>
      ) : (
        <WorkspaceForm
          key={
            activeWorkspace.business_uid
          }
          workspace={activeWorkspace}
          submitLabel="Save settings"
          onSubmit={saveActive}
        />
      )}
    </section>
  );
}

export default WorkspaceSettings;
