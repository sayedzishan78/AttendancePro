import { http } from "./http";

export type RecognitionSettings = {
  recognition_threshold: number;
  live_recognition_stride: number;
  live_recognition_width: number;
};

export const fetchRecognitionSettings = async () => {
  const response = await http.get("/settings/recognition");
  return response.data as RecognitionSettings;
};

export const updateRecognitionSettings = async (payload: RecognitionSettings) => {
  const response = await http.put("/settings/recognition", payload);
  return response.data as RecognitionSettings & { message: string };
};
