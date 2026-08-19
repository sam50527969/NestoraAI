import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  getCurrentAccount,
  loginAccount,
  registerAccount,
} from "../api";

import AuthContext from "./AuthContext";
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "./session";

function AuthProvider({
  children,
}) {
  const [token, setToken] = useState(
    () => getAccessToken(),
  );

  const [user, setUser] =
    useState(null);

  const [
    isLoading,
    setIsLoading,
  ] = useState(Boolean(token));

  const logout = useCallback(() => {
    clearAccessToken();
    setToken(null);
    setUser(null);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    if (!token) {
      setIsLoading(false);
      return undefined;
    }

    let active = true;

    setIsLoading(true);

    getCurrentAccount()
      .then((account) => {
        if (!active) {
          return;
        }

        setUser(account);
      })
      .catch(() => {
        if (!active) {
          return;
        }

        clearAccessToken();
        setToken(null);
        setUser(null);
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [token]);

  const login = useCallback(
    async (credentials) => {
      const response =
        await loginAccount(
          credentials,
        );

      setAccessToken(
        response.access_token,
      );

      setToken(
        response.access_token,
      );

      setUser(response.user);
      setIsLoading(false);

      return response.user;
    },
    [],
  );

  const register = useCallback(
    async (account) => {
      await registerAccount(
        account,
      );

      return login({
        email: account.email,
        password: account.password,
      });
    },
    [login],
  );

  const value = useMemo(
    () => ({
      user,
      token,
      isLoading,
      isAuthenticated: Boolean(
        token && user,
      ),
      login,
      register,
      logout,
    }),
    [
      user,
      token,
      isLoading,
      login,
      register,
      logout,
    ],
  );

  return (
    <AuthContext.Provider
      value={value}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthProvider;