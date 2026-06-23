import { createContext, useState, useEffect, useCallback } from "react";
import { login as apiLogin, getMe } from "../api/auth";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    getMe()
      .then((u) => setUser(u))
      .catch(() => {
        localStorage.removeItem("token");
        setToken(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const login = useCallback(async (username, password) => {
    setError(null);
    try {
      const data = await apiLogin(username, password);
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
      const u = await getMe();
      setUser(u);
      return true;
    } catch (err) {
      const msg =
        err.response?.data?.detail || "Login failed. Please try again.";
      setError(msg);
      return false;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, loading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
