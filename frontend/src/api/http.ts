import axios from "axios";

const DEFAULT_BASE_URL = "http://localhost:8000/api";

const getBaseUrl = () => {
  return localStorage.getItem("attendance_api_base") || import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE_URL;
};

export const http = axios.create({
  baseURL: getBaseUrl(),
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("attendance_token");
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
