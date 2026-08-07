import type { AnalysisResponse, HealthResponse } from "../types/api";

interface ApiErrorBody {
  message?: unknown;
  detail?: unknown;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: AbortSignal.timeout(60_000),
    });
  } catch (error: unknown) {
    if (error instanceof DOMException && error.name === "TimeoutError") {
      throw new Error("A análise excedeu o tempo limite.", { cause: error });
    }
    throw new Error("Não foi possível acessar a API.", { cause: error });
  }
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
    const message =
      typeof body.message === "string"
        ? body.message
        : typeof body.detail === "string"
          ? body.detail
          : "Não foi possível concluir a análise.";
    throw new Error(message);
  }
  return (await response.json()) as T;
}

export const apiClient = {
  analyzeImages(
    files: File[],
    machineId?: string,
    notes?: string,
  ): Promise<AnalysisResponse> {
    const data = new FormData();
    files.forEach((file) => data.append("files", file));
    if (machineId) data.append("machine_id", machineId);
    if (notes) data.append("notes", notes);
    return request<AnalysisResponse>("/v1/analisar", {
      method: "POST",
      body: data,
    });
  },

  healthCheck(): Promise<HealthResponse> {
    return request<HealthResponse>("/health");
  },
};
