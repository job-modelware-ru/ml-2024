import axios from "axios";
import { AuthResponse } from "../models/response/AuthResponse";

export const API_URL = "https://youtube-analytics.ru/api/v1";

const $api = axios.create({
  withCredentials: true,
  baseURL: API_URL,
});

$api.interceptors.request.use((config) => {
  if (localStorage.getItem("token")) {
    config.headers.Authorization = `Bearer ${localStorage.getItem("token")}`;
  }

  return config;
});

$api.interceptors.response.use(
  (config) => {
    return config;
  },
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response.status === 401 &&
      error.config &&
      !error.config._isRetry
    ) {
      originalRequest._isRetry = true;
      try {
        const response = await axios.post<AuthResponse>(
          `${API_URL}/refresh/`,
          {},
          {
            withCredentials: true,
          }
        );
        localStorage.setItem("token", response.data.token);
        return $api.request(originalRequest);
      } catch (e: any) {
        console.log(e.response?.data?.message);
      }
    }
    throw error;
  }
);

export default $api;
