import {
  Navigate,
  Outlet,
  useLocation,
} from "react-router-dom";

import useAuth from "./useAuth";

function ProtectedRoute() {
  const location = useLocation();

  const {
    isAuthenticated,
    isLoading,
  } = useAuth();

  if (isLoading) {
    return (
      <div className="auth-loading-screen">
        <div className="auth-loading-spinner" />

        <p>
          Restoring your Nestora session...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location,
        }}
      />
    );
  }

  return <Outlet />;
}

export default ProtectedRoute;