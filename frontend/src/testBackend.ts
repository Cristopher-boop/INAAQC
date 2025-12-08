import { api } from "./lib/api";

export async function testBackend() {
  try {
    const res = await api.get("/"); // tu backend debería responder algo
    console.log("Backend conectado:", res.data);
  } catch (error) {
    console.error("Error al conectar backend:", error);
  }
}
