# 🧠 Agentic Log Observer System (MVP) - Log Monitoring Tool powered by AI

A lightweight, agentic-AI powered log analysis system designed to analyze, summarize, and intelligently interpret large JSON log files (e.g., Azure Function, API, WebApp logs). Built using **FastAPI**, **LangChain**, and **Phi-3 (via Ollama)** — optimized for speed, clarity, and real-world debugging.

---

## 📦 Features

- 🔍 Upload & parse JSON log files (`sample_log.json`)
- 🧠 Automatically summarize each **Error** and **Warning** using a local LLM
- 🧾 Structured AI summary includes:
  - Error title
  - Root cause
  - Stack info
  - Fix suggestions
- ⚡ Super-fast inference using **Phi-3 via Ollama**
- ✅ Designed for demo, but scalable for production

---

## ⚙️ Tech Stack

| Layer     | Tool / Framework        |
|-----------|-------------------------|
| Backend   | FastAPI                 |
| LLM       | Phi-3 via Ollama (local)|
| AI Agent  | LangChain (LLMChain)    |
| Parser    | Python (custom grouping logic) |
| Deployment Ready | Render, Railway, or VPS |

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/agentic-log-monitor.git
cd agentic-log-monitor
```

### 2. Set up Python environment
```bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

### 3. Start Ollama with Phi-3
```bash
ollama run phi3
```

### 4. Run FastAPI backend
```bash
uvicorn app.main:app --reload
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📽️ Demo

A short demo video recording of this system availabe in demo folder

## 💡 Example Summary Output

```json
{
  "error_title": "NullReferenceException",
  "error_code": null,
  "description": "A null object was accessed during execution.",
  "stack_info": "Function.Run() at line 42",
  "probable_cause": "Missing null check",
  "suggested_fix": "Add guard clause before accessing variable"
}
```

---

## 🎯 Use Case

> Designed for engineering teams who spend hours debugging unstructured logs from APIs, WebApps, or serverless functions. This tool speeds up root cause analysis by intelligently summarizing incidents and helping triage problems faster.

---

## 🌱 Future Improvements

- [ ] Web UI with live upload + summary view
- [ ] Async LLM tasks with job ID and polling
- [ ] Historical error tracking and trend detection
- [ ] Vector DB + RAG for root-cause suggestions
- [ ] CI/CD + containerization for deployment

---

## 📄 License

MIT License – Free to use, modify, and extend.

---

**Built by:** *Ramaprasath Appaiah*  
_“Debug faster, think deeper, fix smarter — with AI.”_