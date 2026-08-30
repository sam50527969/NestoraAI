import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  createWorkspace as createWorkspaceRequest,
  getWorkspaces,
  updateWorkspace as updateWorkspaceRequest,
} from "../api/workspaces";
import useAuth from "../auth/useAuth";

import WorkspaceContext from "./WorkspaceContext";

function storageKey(userUid) {
  return `nestora.active_workspace.${userUid}`;
}

function WorkspaceProvider({
  children,
}) {
  const {
    user,
    isAuthenticated,
  } = useAuth();

  const [
    workspaces,
    setWorkspaces,
  ] = useState([]);

  const [
    activeWorkspace,
    setActiveWorkspace,
  ] = useState(null);

  const [
    isLoading,
    setIsLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState(null);

  const userUid = user?.user_uid;

  const rememberWorkspace =
    useCallback(
      (workspace) => {
        setActiveWorkspace(workspace);

        if (workspace && userUid) {
          window.localStorage.setItem(
            storageKey(userUid),
            workspace.business_uid,
          );
        }
      },
      [userUid],
    );

  const refreshWorkspaces =
    useCallback(async () => {
      if (
        !isAuthenticated ||
        !userUid
      ) {
        setWorkspaces([]);
        setActiveWorkspace(null);
        setError(null);
        setIsLoading(false);
        return [];
      }

      setIsLoading(true);
      setError(null);

      try {
        const response =
          await getWorkspaces();

        const available =
          response.businesses;

        const storedUid =
          window.localStorage.getItem(
            storageKey(userUid),
          );

        const selected =
          available.find(
            (workspace) =>
              workspace.business_uid
              === storedUid,
          )
          || available[0]
          || null;

        setWorkspaces(available);
        setActiveWorkspace(selected);

        if (selected) {
          window.localStorage.setItem(
            storageKey(userUid),
            selected.business_uid,
          );
        } else {
          window.localStorage.removeItem(
            storageKey(userUid),
          );
        }

        return available;
      } catch (loadError) {
        setWorkspaces([]);
        setActiveWorkspace(null);
        setError(loadError);
        return [];
      } finally {
        setIsLoading(false);
      }
    }, [
      isAuthenticated,
      userUid,
    ]);

  useEffect(() => {
    refreshWorkspaces();
  }, [refreshWorkspaces]);

  const selectWorkspace =
    useCallback(
      (businessUid) => {
        const selected =
          workspaces.find(
            (workspace) =>
              workspace.business_uid
              === businessUid,
          );

        if (!selected || !userUid) {
          return false;
        }

        rememberWorkspace(selected);
        return true;
      },
      [
        workspaces,
        userUid,
        rememberWorkspace,
      ],
    );

  const createWorkspace =
    useCallback(
      async (workspace) => {
        const created =
          await createWorkspaceRequest(
            workspace,
          );

        setWorkspaces(
          (current) => [
            created,
            ...current.filter(
              (item) =>
                item.business_uid
                !== created.business_uid,
            ),
          ],
        );

        rememberWorkspace(created);
        setError(null);

        return created;
      },
      [rememberWorkspace],
    );

  const updateWorkspace =
    useCallback(
      async (
        businessUid,
        workspace,
      ) => {
        const updated =
          await updateWorkspaceRequest(
            businessUid,
            workspace,
          );

        setWorkspaces(
          (current) =>
            current.map((item) =>
              item.business_uid
                === updated.business_uid
                ? updated
                : item,
            ),
        );

        if (
          activeWorkspace?.business_uid
          === updated.business_uid
        ) {
          rememberWorkspace(updated);
        }

        setError(null);

        return updated;
      },
      [
        activeWorkspace,
        rememberWorkspace,
      ],
    );

  const value = useMemo(
    () => ({
      workspaces,
      activeWorkspace,
      activeBusinessUid:
        activeWorkspace?.business_uid
        || null,
      isLoading,
      error,
      hasWorkspaces:
        workspaces.length > 0,
      selectWorkspace,
      createWorkspace,
      updateWorkspace,
      refreshWorkspaces,
    }),
    [
      workspaces,
      activeWorkspace,
      isLoading,
      error,
      selectWorkspace,
      createWorkspace,
      updateWorkspace,
      refreshWorkspaces,
    ],
  );

  return (
    <WorkspaceContext.Provider
      value={value}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export default WorkspaceProvider;
