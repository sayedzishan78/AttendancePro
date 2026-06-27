import { http } from "./http";
import { PersonType } from "./persons";

export type AttendanceRecord = {
  id: number;
  person_id: number;
  name: string;
  person_type: PersonType;
  date: string;
  check_in_time: string;
  check_out_time?: string | null;
  confidence: number;
  total_detections: number;
  duration_minutes?: number | null;
  image_path?: string | null;
};

export const fetchAttendance = async (params?: {
  start_date?: string;
  end_date?: string;
  person_id?: number;
  person_type?: PersonType;
}) => {
  const response = await http.get("/attendance", { params });
  return response.data as { count: number; records: AttendanceRecord[] };
};

export const fetchAttendanceSummary = async (date?: string) => {
  const response = await http.get("/attendance/summary", {
    params: date ? { target_date: date } : undefined,
  });
  return response.data as {
    date: string;
    total_people: number;
    present: number;
    attendance_rate: number;
  };
};
