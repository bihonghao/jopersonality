# Resume Agent Frontend

Minimal React + Vite + TypeScript + Tailwind UI for testing the Resume Agent backend.

## Setup

```bash
npm install
```

Create a `.env` file in `frontend/`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Run Development Server

```bash
npm run dev
```

App runs by default at `http://localhost:5173`.

## OpenAI Key Setup Flow (Local Dev)

1. Open the app.
2. If backend key is missing or invalid, you'll see **OpenAI API Key Not Configured**.
3. Enter your key in the masked password field.
4. Click **Save Key**.
5. The frontend calls `POST /settings/openai-key`, backend stores the key in local backend `.env`, then app reloads.

## Usage

1. Choose a resume file (`.pdf`, `.docx`, `.txt`).
2. Click **Upload and Analyze**.
3. Review parsed candidate sections and raw JSON response.

## Notes

- Backend endpoint used: `POST /resume/analyze`
- Settings endpoints: `GET /settings/status`, `POST /settings/openai-key`
- Ensure backend is running and CORS allows `http://localhost:5173`.
