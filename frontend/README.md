# AI Startup Validator — React Frontend

## Quick Start

### Step 1: Install Node.js (one time only)
Download and install from: **https://nodejs.org/en/download** (choose LTS version)
> After install, restart your terminal/PowerShell

### Step 2: Start the FastAPI backend
```powershell
# Open Terminal 1
cd "c:\Users\jilan\OneDrive\Desktop\Startup Validator"
.\venv\Scripts\activate
uvicorn fast_api:app --reload --port 8000
```

### Step 3: Install frontend dependencies & start React
```powershell
# Open Terminal 2
cd "c:\Users\jilan\OneDrive\Desktop\Startup Validator\frontend"
npm install
npm run dev
```

### Step 4: Open in browser
Go to: **http://localhost:5173**

---

## Project Structure

```
Startup Validator/
├── fast_api.py          ← FastAPI backend (UNCHANGED)
├── agents.py            ← Agent logic (UNCHANGED)
├── .env                 ← API keys (UNCHANGED)
└── frontend/
    ├── package.json
    ├── vite.config.js   ← Proxies /analyze, /status → :8000
    ├── .env             ← VITE_API_BASE=http://localhost:8000
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx          ← Main state + 2s polling loop
        ├── api.js           ← submitIdea() + pollStatus()
        ├── index.css        ← Full dark design system
        └── components/
            ├── Header.jsx
            ├── IdeaForm.jsx
            ├── ProgressBar.jsx
            ├── ResultCards.jsx
            ├── LandingPagePreview.jsx
            ├── FullReport.jsx
            └── Sidebar.jsx
```

## What Maps to What (Streamlit → React)

| Streamlit | React |
|-----------|-------|
| `submit_idea()` | `api.js → submitIdea()` |
| `poll_status()` | `api.js → pollStatus()` |
| `while True: time.sleep(2)` | `setInterval(fn, 2000)` in App.jsx |
| `st.session_state` | `useState(INITIAL_STATE)` in App.jsx |
| `st.progress()` + `st.empty()` | `<ProgressBar />` component |
| `card(title, content)` | `<ResultCards />` component |
| `st.expander()` | `<FullReport />` collapsible |
| `st.download_button()` | Download button in `<FullReport />` |
| `st.sidebar` | `<Sidebar />` component |
| Landing page (commented out) | `<LandingPagePreview />` iframe |
