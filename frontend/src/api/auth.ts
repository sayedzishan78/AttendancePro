import { http } from "./http";

export const login = async (username: string, password: string) => {
  const response = await http.post("/auth/login", { username, password });
  return response.data as { access_token: string; token_type: string; role: "admin" | "staff" | "student" };
};

export const me = async () => {
  const response = await http.get("/auth/me");
  return response.data as { role: "admin" | "staff" | "student"; is_active: boolean };
};

export const register = async (payload: {
  full_name: string;
  email: string;
  password: string;
  role: "staff" | "student";
  department?: string;
  note?: string;
}) => {
  const response = await http.post("/auth/register", payload);
  return response.data as { message: string; id: number; role: "staff" | "student" };
};
