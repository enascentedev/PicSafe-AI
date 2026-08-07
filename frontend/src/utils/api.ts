import axios from "axios";
import type { AnalysisResponse, HealthResponse } from "../types/api";

// Configuração da API
// Em desenvolvimento, usa o proxy do Vite (/api)
// Em produção, usa a variável de ambiente ou padrão
const API_BASE_URL =
  import.meta.env.VITE_API_URL ||
  (import.meta.env.DEV ? "/api" : "http://localhost:8000");

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 segundos
});

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 400) {
      throw new Error(error.response.data.detail || "Dados inválidos");
    }
    if (error.response?.status === 500) {
      throw new Error("Erro interno do servidor. Tente novamente.");
    }
    if (error.code === "ECONNABORTED") {
      throw new Error("Tempo limite excedido. Verifique sua conexão.");
    }
    throw new Error(error.message || "Erro desconhecido");
  }
);

export const apiClient = {
  // Análise de imagens
  async analyzeImages(
    files: File[],
    machineId?: string,
    notes?: string
  ): Promise<AnalysisResponse> {
    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    if (machineId) formData.append("machine_id", machineId);
    if (notes) formData.append("notes", notes);

    const response = await api.post<AnalysisResponse>(
      "/v1/analisar",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  },

  // Verificação de saúde
  async healthCheck(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>("/health");
    return response.data;
  },

  // Página inicial
  async getHomePage(): Promise<string> {
    const response = await api.get<string>("/");
    return response.data;
  },
};

export default apiClient;
