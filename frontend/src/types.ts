export interface ExperienceItem {
  company: string;
  title: string;
  start_date: string;
  end_date: string;
  responsibilities: string[];
  tools: string[];
}

export interface CandidateProfile {
  name: string;
  email: string;
  phone: string;
  location: string;
  summary: string;
  skills: string[];
  experience: ExperienceItem[];
  education: string[];
  certifications: string[];
  projects: string[];
  estimated_years_experience: number;
  seniority_level: string;
  career_signals: string[];
  missing_info: string[];
}

export type KeyStatus = "configured" | "missing" | "invalid";

export interface SettingsStatus {
  openai_configured: boolean;
  key_status: KeyStatus;
}
