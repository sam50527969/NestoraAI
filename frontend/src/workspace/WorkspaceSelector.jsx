import useWorkspace from "./useWorkspace";

function WorkspaceSelector() {
  const {
    workspaces,
    activeBusinessUid,
    isLoading,
    selectWorkspace,
  } = useWorkspace();

  if (
    isLoading ||
    workspaces.length === 0
  ) {
    return null;
  }

  return (
    <label className="workspace-selector">
      <span className="workspace-selector-label">
        Active workspace
      </span>

      <select
        aria-label="Active workspace"
        value={activeBusinessUid || ""}
        onChange={(event) => {
          selectWorkspace(
            event.target.value,
          );
        }}
      >
        {workspaces.map(
          (workspace) => (
            <option
              key={
                workspace.business_uid
              }
              value={
                workspace.business_uid
              }
            >
              {workspace.name}
            </option>
          ),
        )}
      </select>
    </label>
  );
}

export default WorkspaceSelector;
