import axios from "axios";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000", // cambia si tu backend usa otro puerto
  headers: {
    "Content-Type": "application/json",
  },
});

// Ejemplo de interceptores (opcional para auth)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
