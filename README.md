# SHL Intel | AI Assessment Recommender

An AI-powered agentic assistant designed to recommend and compare candidate hiring assessments grounded directly in the official **SHL Product Catalog**. Built with a premium, responsive UI following SHL’s visual standards, a high-performance **FastAPI** backend, and **FAISS** semantic vector search.

---

## 🚀 Key Features

* **Agentic RAG Engine**: Combines **Sentence-Transformers** for semantic catalog embedding with **Groq LLaMA 3.3** to deliver interactive, highly accurate role-to-assessment matching.
* **Sub-Millisecond Boot Time**: Loads FAISS index binary (`index.faiss`) instantly from disk, completely eliminating cold-start encoding spikes on CPU environments.
* **Clean, Modular Architecture**: Fully separated HTML markup, CSS stylesheet variables, and JavaScript state-management logic for developer-grade version control.
* **Dynamic Host Auto-Detection**: JavaScript dynamically falls back to `localhost` when loaded locally (via dev server or direct `file://` execution) and auto-switches to production host once deployed.
* **Stateless Turn Management**: Transparent turn indicator UI displaying active conversation counts with a strict **8-turn maximum conversation window**.
* **Visual Excellence**: Premium dark-green brand-aligned aesthetic, fluid hover micro-animations, glassmorphism, responsive mobile layouts, and instant typing indicator feedback.

---

## 📁 Project Structure

```text
├── shl_frontend.html      # Modular HTML markup (layout, SVGs, structural shells)
├── style.css              # Custom CSS stylesheet (design tokens, layout, hover effects)
├── app.js                 # Frontend application logic (state, API hooks, environment detection)
├── LICENSE                # MIT Open-Source License
├── .gitignore             # Git-ignored folders (virtualenvs, cache folders)
├── README.md              # Project documentation
│
└── shl-recommender/       # FastAPI Backend Application
    ├── main.py            # API controller and endpoint setup
    ├── agent.py           # LLM agent system and prompts
    ├── vector_store.py    # Semantic search index handlers
    ├── scraper.py         # Catalog preprocessing pipeline
    ├── precompute_index.py# FAISS vector builder script
    ├── catalog.json       # Cleaned SHL catalog database
    ├── index.faiss        # Compiled FAISS index binary
    ├── Dockerfile         # Production single-stage Docker blueprint
    └── requirements.txt   # Backend python dependencies
```

---

## 💻 Local Setup & Execution

### 1. Run the FastAPI Backend
Ensure Python 3.10+ is installed on your system.

```bash
# Navigate to the backend directory
cd shl-recommender

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Pre-compile the FAISS index (if index.faiss is not present)
python precompute_index.py

# Start the local development server
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Run the Frontend
Simply double-click or open the **`shl_frontend.html`** file in any modern browser! The page will dynamically identify that it is running locally and link to your local FastAPI backend.

---

## 🐳 Docker Deployment

The application is completely containerized and optimized for cloud platforms (e.g. Render, Fly.io, AWS, DigitalOcean).

```bash
# Build the production Docker image
docker build -t shl-intel-agent:latest ./shl-recommender

# Run the container locally
docker run -d -p 8000:8000 shl-intel-agent:latest
```

---

## 📄 License
This project is licensed under the permissive **MIT License** — see the [LICENSE](LICENSE) file for complete details.
