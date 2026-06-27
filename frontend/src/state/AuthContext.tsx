import React, { createContext, useContext, useMemo, useState } from "react";

type AuthContextValue = {
  token: string | null;
  setToken: (token: string | null) => void;
  role: "admin" | "staff" | "student";
  setRole: (role: "admin" | "staff" | "student") => void;
  isAuthenticated: boolean;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const TOKEN_KEY = "attendance_token";
const ROLE_KEY = "attendance_role";

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setTokenState] = useState<string | null>(
    localStorage.getItem(TOKEN_KEY)
  );
  const [role, setRoleState] = useState<"admin" | "staff" | "student">(
    (localStorage.getItem(ROLE_KEY) as "admin" | "staff" | "student") || "staff"
  );

  const setToken = (value: string | null) => {
    if (value) {
      localStorage.setItem(TOKEN_KEY, value);
    } else {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(ROLE_KEY);
      setRoleState("staff");
    }
    setTokenState(value);
  };

  const setRole = (value: "admin" | "staff" | "student") => {
    localStorage.setItem(ROLE_KEY, value);
    setRoleState(value);
  };

  const value = useMemo(
    () => ({
      token,
      setToken,
      role,
      setRole,
      isAuthenticated: Boolean(token),
    }),
    [token, role]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};
