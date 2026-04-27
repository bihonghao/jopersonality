import { useEffect, useMemo, useState } from "react";
import axios from "axios";

import { analyzeResume, getSettingsStatus, saveOpenAIKey } from "./api";
import type { CandidateProfile, KeyStatus } from "./types";

const allowedTypes = [
  "application/pdf",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain",
];

function renderList(items: string[]) {
  if (!items.length) {
    return <p className="text-sm text-slate-500">None</p>;
  }

  return (
    <ul className="list-disc space-y-1 pl-5 text-sm">
      {items.map((item, idx) => (
        <li key={`${item}-${idx}`}>{item}</li>
      ))}
    </ul>
  );
}

function keyStatusClasses(keyStatus: KeyStatus): string {
  if (keyStatus === "configured") return "bg-emerald-100 text-emerald-700";
  if (keyStatus === "invalid") return "bg-amber-100 text-amber-700";
  return "bg-slate-200 text-slate-700";
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CandidateProfile | null>(null);

  const [settingsLoading, setSettingsLoading] = useState(true);
  const [keyStatus, setKeyStatus] = useState<KeyStatus>("missing");
  const [keyInput, setKeyInput] = useState("");
  const [savingKey, setSavingKey] = useState(false);
  const [settingsError, setSettingsError] = useState<string | null>(null);

  const refreshSettings = async () => {
    try {
      const status = await getSettingsStatus();
      setKeyStatus(status.key_status);
      setSettingsError(null);
    } catch {
      setSettingsError("Unable to load settings status.");
    } finally {
      setSettingsLoading(false);
    }
  };

  useEffect(() => {
    void refreshSettings();
  }, []);

  const fileSummary = useMemo(() => {
    if (!file) {
      return "No file selected";
    }
    return `${file.name} (${Math.ceil(file.size / 1024)} KB)`;
  }, [file]);

  const validateFile = (candidate: File | null): string | null => {
    if (!candidate) {
      return "Please select a resume file before uploading.";
    }

    const extension = candidate.name.split(".").pop()?.toLowerCase();
    if (!extension || !["pdf", "docx", "txt"].includes(extension)) {
      return "Unsupported file type. Please upload a PDF, DOCX, or TXT file.";
    }

    if (!allowedTypes.includes(candidate.type) && candidate.type !== "") {
      return "The selected file MIME type is unsupported.";
    }

    if (candidate.size === 0) {
      return "The selected file is empty.";
    }

    return null;
  };

  const onSaveKey = async () => {
    if (!keyInput.trim()) {
      setSettingsError("Please enter an API key.");
      return;
    }

    setSavingKey(true);
    setSettingsError(null);

    try {
      await saveOpenAIKey(keyInput);
      setKeyInput("");
      setSettingsLoading(true);
      await refreshSettings();
      window.location.reload();
    } catch (saveError) {
      if (axios.isAxiosError(saveError)) {
        setSettingsError(saveError.response?.data?.detail || "Failed to save API key.");
      } else {
        setSettingsError("Unexpected settings save error.");
      }
    } finally {
      setSavingKey(false);
    }
  };

  const onUpload = async () => {
    const validationMessage = validateFile(file);
    if (validationMessage) {
      setError(validationMessage);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await analyzeResume(file as File);
      if (!data || Object.keys(data).length === 0) {
        setError("Backend returned an empty response.");
        setResult(null);
        return;
      }

      setResult(data);
    } catch (uploadError) {
      if (axios.isAxiosError(uploadError)) {
        const detail = uploadError.response?.data?.detail;
        setError(detail || "Unable to analyze resume. Please try again.");
      } else {
        setError("Unexpected upload error occurred.");
      }
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  if (settingsLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center p-6">
        <div className="rounded-xl bg-white p-6 shadow">Loading settings...</div>
      </main>
    );
  }

  return (
    <main className="mx-auto min-h-screen max-w-5xl p-4 sm:p-8">
      <section className="mx-auto mb-6 max-w-2xl rounded-xl bg-white p-6 shadow">
        <div className="mb-4 flex items-center justify-between gap-3">
          <h1 className="text-2xl font-bold">Resume Agent Dashboard</h1>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ${keyStatusClasses(keyStatus)}`}>
            {keyStatus}
          </span>
        </div>

        {settingsError && <p className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{settingsError}</p>}

        {keyStatus !== "configured" ? (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">OpenAI API Key Not Configured</h2>
            <p className="text-sm text-slate-600">
              Save your OpenAI API key locally for development. The key is stored in your local backend `.env` file and is never shown back in full.
            </p>
            <label className="block text-sm font-medium text-slate-700" htmlFor="openai-key">
              OpenAI API Key
            </label>
            <input
              id="openai-key"
              type="password"
              value={keyInput}
              onChange={(event) => setKeyInput(event.target.value)}
              placeholder="sk-..."
              className="block w-full rounded border border-slate-300 bg-slate-50 p-2 text-sm"
            />
            <button
              type="button"
              onClick={onSaveKey}
              disabled={savingKey}
              className="rounded bg-indigo-600 px-4 py-2 text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {savingKey ? "Saving..." : "Save Key"}
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-sm text-slate-600">Upload a PDF, DOCX, or TXT resume to parse structured candidate data.</p>

            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={(event) => {
                const selected = event.target.files?.[0] || null;
                setFile(selected);
                setError(null);
              }}
              className="block w-full rounded border border-slate-300 bg-slate-50 p-2 text-sm"
            />

            <p className="text-sm text-slate-600">{fileSummary}</p>

            <button
              type="button"
              onClick={onUpload}
              disabled={loading}
              className="rounded bg-indigo-600 px-4 py-2 text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? "Analyzing..." : "Upload and Analyze"}
            </button>

            {error && <p className="rounded bg-red-50 p-2 text-sm text-red-700">{error}</p>}
          </div>
        )}
      </section>

      {keyStatus === "configured" && result && (
        <section className="space-y-4 rounded-xl bg-white p-6 shadow">
          <h2 className="text-xl font-semibold">Parsed Resume Result</h2>

          <div className="grid gap-4 sm:grid-cols-2">
            <div><p className="font-medium">Name</p><p>{result.name || "-"}</p></div>
            <div><p className="font-medium">Email</p><p>{result.email || "-"}</p></div>
            <div><p className="font-medium">Phone</p><p>{result.phone || "-"}</p></div>
            <div><p className="font-medium">Location</p><p>{result.location || "-"}</p></div>
            <div className="sm:col-span-2"><p className="font-medium">Summary</p><p>{result.summary || "-"}</p></div>
            <div><p className="font-medium">Estimated Years Experience</p><p>{result.estimated_years_experience ?? 0}</p></div>
            <div><p className="font-medium">Seniority Level</p><p>{result.seniority_level || "-"}</p></div>
          </div>

          <div>
            <p className="font-medium">Skills</p>
            {renderList(result.skills)}
          </div>

          <div>
            <p className="font-medium">Experience</p>
            {!result.experience.length ? (
              <p className="text-sm text-slate-500">None</p>
            ) : (
              <div className="space-y-3">
                {result.experience.map((exp, idx) => (
                  <article key={`${exp.company}-${idx}`} className="rounded border border-slate-200 p-3">
                    <p className="font-semibold">{exp.title || "-"} @ {exp.company || "-"}</p>
                    <p className="text-sm text-slate-600">{exp.start_date || "-"} - {exp.end_date || "-"}</p>
                    <div className="mt-2">
                      <p className="text-sm font-medium">Responsibilities</p>
                      {renderList(exp.responsibilities)}
                    </div>
                    <div className="mt-2">
                      <p className="text-sm font-medium">Tools</p>
                      {renderList(exp.tools)}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div><p className="font-medium">Education</p>{renderList(result.education)}</div>
            <div><p className="font-medium">Certifications</p>{renderList(result.certifications)}</div>
            <div><p className="font-medium">Projects</p>{renderList(result.projects)}</div>
            <div><p className="font-medium">Career Signals</p>{renderList(result.career_signals)}</div>
            <div className="sm:col-span-2"><p className="font-medium">Missing Info</p>{renderList(result.missing_info)}</div>
          </div>

          <details>
            <summary className="cursor-pointer text-sm font-medium text-indigo-700">View Raw JSON</summary>
            <pre className="mt-2 overflow-auto rounded bg-slate-900 p-3 text-xs text-slate-100">
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </section>
      )}
    </main>
  );
}
