import { http } from "./http";

export type PersonType = "student" | "staff";

export type Person = {
  id: number;
  name: string;
  email?: string | null;
  department?: string | null;
  person_code?: string | null;
  person_type: PersonType;
};

export const fetchPersons = async (personType?: PersonType) => {
  const response = await http.get("/persons", {
    params: personType ? { person_type: personType } : undefined,
  });
  return response.data as { count: number; persons: Person[] };
};

export const createPerson = async (payload: Omit<Person, "id" | "is_active">) => {
  const response = await http.post("/persons", payload);
  return response.data as { id: number; name: string };
};

export const updatePerson = async (id: number, payload: Partial<Person>) => {
  const response = await http.patch(`/persons/${id}`, payload);
  return response.data as { message: string; id: number };
};

export const deactivatePerson = async (id: number) => {
  const response = await http.delete(`/persons/${id}`);
  return response.data as { message: string; id: number };
};

export const trainPerson = async (payload: {
  person_id: number;
  name: string;
  person_type: PersonType;
  email?: string;
  department?: string;
  person_code?: string;
  files: File[];
}) => {
  const form = new FormData();
  form.append("person_id", String(payload.person_id));
  form.append("name", payload.name);
  form.append("person_type", payload.person_type);
  if (payload.email) form.append("email", payload.email);
  if (payload.department) form.append("department", payload.department);
  if (payload.person_code) form.append("person_code", payload.person_code);
  payload.files.forEach((file) => form.append("files", file));

  const response = await http.post("/train/", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};
