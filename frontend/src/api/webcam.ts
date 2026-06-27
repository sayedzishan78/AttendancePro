import { http } from "./http";

export const startMonitoring = async (camera_id = 0, save_images = true) => {
  const response = await http.post("/webcam/start/", null, {
    params: { camera_id, save_images },
  });
  return response.data;
};

export const stopMonitoring = async () => {
  const response = await http.post("/webcam/stop/");
  return response.data;
};

export const fetchStatus = async () => {
  const response = await http.get("/webcam/status/");
  return response.data;
};

export const fetchPreview = async () => {
  const response = await http.get("/webcam/preview/");
  return response.data as {
    frame_base64: string;
    timestamp: string;
    recognition_results: Array<{
      name: string;
      person_id: number | null;
      confidence: number;
      recognized: boolean;
      bbox: number[];
    }>;
  };
};
