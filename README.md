# Resume Agent (jopersonality)

Production-ready FastAPI service that accepts resume uploads (`.pdf`, `.docx`, `.txt`), extracts text, uses OpenAI to normalize candidate data, and returns structured JSON for downstream career matching agents.

## Project Structure

```text
jopersonality/
  backend/
    agents/
      resume_agent.py
    services/
      resume_parser.py
    schemas/
      candidate_profile.py
    main.py
    requirements.txt
```

## Installation

1. Create a Python 3.11 virtual environment.
2. Install dependencies.
3. Configure environment variables.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Run Server

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoint

### `POST /resume/analyze`

- Content type: `multipart/form-data`
- Field name: `file`
- Supported extensions: `pdf`, `docx`, `txt`

### Curl Example

```bash
curl -X POST "http://localhost:8000/resume/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@./sample_resume.pdf"
```

## Sample Output

```json
{
  "name": "Jane Doe",
  "email": "jane.doe@email.com",
  "phone": "+1-555-0101",
  "location": "Austin, TX",
  "summary": "Backend engineer with 6 years of experience building cloud APIs.",
  "skills": ["Python", "FastAPI", "PostgreSQL", "AWS", "Docker"],
  "experience": [
    {
      "company": "Acme Corp",
      "title": "Senior Software Engineer",
      "start_date": "2021-01",
      "end_date": "Present",
      "responsibilities": [
        "Built and maintained high-throughput APIs",
        "Mentored junior engineers"
      ],
      "tools": ["FastAPI", "Terraform", "Kubernetes"]
    }
  ],
  "education": ["B.S. Computer Science - University of Texas"],
  "certifications": ["AWS Certified Developer"],
  "projects": ["Resume Scoring Platform"],
  "estimated_years_experience": 6,
  "seniority_level": "Senior",
  "career_signals": ["Backend specialization", "Leadership experience"],
  "missing_info": []
}
```

## Error Handling Included

- Unsupported file types
- Empty file uploads
- Parsing failures for PDF/DOCX/TXT
- Missing `OPENAI_API_KEY`
- Invalid/non-JSON model output
- Schema validation failures
