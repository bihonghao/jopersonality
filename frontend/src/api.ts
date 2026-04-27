import axios from "axios";
import type { CandidateProfile, SettingsStatus } from "./types";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  timeout: 60000,
});

export async function analyzeResume(file: File): Promise<CandidateProfile> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await apiClient.post<CandidateProfile>("/resume/analyze", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
}

export async function getSettingsStatus(): Promise<SettingsStatus> {
  const response = await apiClient.get<SettingsStatus>("/settings/status");
  return response.data;
}

export async function saveOpenAIKey(openaiApiKey: string): Promise<void> {
  await apiClient.post("/settings/openai-key", {
    openai_api_key: openaiApiKey,
  });
}
