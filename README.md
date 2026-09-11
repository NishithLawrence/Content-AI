# ContentAI

## Overview

AI-powered social media content planning platform that generates industry-specific content calendars using reference materials.

## Features

- **Industry-Specific Content Strategy**: Tailored strategy frameworks for:
  - Real Estate
  - Jewellery
  - Perfume
  - FMCG / Food
- **Flexible Plan Durations & Post Counts**:
  - 1 Week (3 posts)
  - 2 Weeks (6 posts)
  - 1 Month (12 posts)
- **Multi-Platform Support**:
  - Instagram
  - LinkedIn
  - Facebook
- **Reference File Intelligence**: Factual grounding against uploaded brand/product documents.
- **Structured Post Outputs**: Includes AI-generated captions, visual creative direction, and targeted hashtags.
- **Single-Post Regeneration**: Regenerate individual posts without altering the rest of the calendar.
- **Copy & Export Functionality**: Easy copying and JSON export of generated content plans.

## Supported Reference Files

- **Documents**: PDF (`.pdf`), Word (`.doc`, `.docx`), PowerPoint (`.ppt`, `.pptx`), Excel (`.xls`, `.xlsx`), Text (`.txt`)
- **Images**: JPG (`.jpg`), JPEG (`.jpeg`), PNG (`.png`)

## Architecture

- **Frontend**: React + Vite
- **Backend**: FastAPI + Python (Uvicorn)
- **AI Integration**: OpenAI-compatible API (OpenAI / Gemini OpenAI endpoint)
- **Reference File Processing**: `pypdf`, `python-docx`, `python-pptx`, `openpyxl`, `Pillow`

## Project Structure

```text
AI_Content_platform/
├── Backend/
│   ├── app/
│   │   ├── api/                # FastAPI routers (health, generate, regenerate)
│   │   ├── core/               # Industry strategies & configuration
│   │   ├── file_processing/    # Multi-format document context extraction
│   │   ├── models/             # Pydantic schemas for requests and responses
│   │   └── services/           # AI service layer (OpenAI integration & prompts)
│   ├── test_api.py             # API validation & core flow tests
│   ├── test_reference_files.py # Document extraction & grounding tests
│   ├── test_phase4_dashboard.py# Single post regeneration endpoint test
│   ├── test_e2e_full_qa.py     # Full end-to-end integration test
│   ├── .env.example            # Environment variable configuration template
│   ├── requirements.txt        # Backend dependencies
│   └── run.py                  # Backend server entry point
├── Frontend/
│   ├── src/
│   │   ├── components/         # React UI components (Form, Strategy, Calendar, PostCard)
│   │   ├── App.jsx             # Main Application container
│   │   └── App.css             # Glassmorphism design system & styling
│   ├── package.json            # Frontend dependencies & scripts
│   └── vite.config.js          # Vite server & build configuration
├── .gitignore                  # Git repository exclusion rules
└── README.md                   # Project documentation
```

## Setup

### 1. Backend Setup

```bash
cd Backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd Frontend
npm install
```

## Environment Variables

Copy `Backend/.env.example` to `Backend/.env` and configure your API key:

```bash
# Backend/.env
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Gemini OpenAI-compatibility setup
# GEMINI_API_KEY=your_gemini_api_key_here
# OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
# AI_MODEL_NAME=gemini-2.5-flash
```

> [!IMPORTANT]
> Never commit your `.env` file or expose your API keys in source code.

## Run Locally

### Start Backend Server

```bash
cd Backend
python run.py
```

The backend server will run on `http://localhost:8000`.

### Start Frontend Dev Server

```bash
cd Frontend
npm run dev
```

The frontend application will run on `http://localhost:5173`.

## API Endpoints

- `GET /api/health`: Health check endpoint. Returns operational status.
- `POST /api/generate-content`: Generates structured social media content plan (accepts JSON or `multipart/form-data` with optional reference files).
- `POST /api/regenerate-post`: Regenerates a single post in an existing content calendar while preserving strategy and reference context.

## Testing

Run backend unit and integration test suites:

```bash
# API & validation tests
python Backend/test_api.py

# Reference file extraction & grounding tests
python Backend/test_reference_files.py

# Single-post regeneration tests
python Backend/test_phase4_dashboard.py

# Full end-to-end QA test suite
python Backend/test_e2e_full_qa.py
```

## Security

- API keys are maintained exclusively on the server side in environment variables (`.env`).
- `.env` and `.env.*` files are explicitly excluded via `.gitignore` to prevent secret leakage.
- Sanitized exception handling prevents internal API keys from exposing in runtime error responses.

## Demo

Live Deployment: *[Deployment URL Placeholder]*
