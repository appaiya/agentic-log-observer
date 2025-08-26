# app/main.py
import os, json, uuid, asyncio
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.services.log_analyzer import analyze_logs
from app.agents.llm_summary_agent import summarize_each_error

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

JOBS: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def upload_page(request: Request):
    # still serve index.html via templates, but we’ll fetch()/AJAX the form
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_log(file: UploadFile = File(...)):
    # stream-save big files to avoid long pending request
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    import aiofiles
    CHUNK = 1024 * 1024
    async with aiofiles.open(file_path, "wb") as out:
        while True:
            chunk = await file.read(CHUNK)
            if not chunk:
                break
            await out.write(chunk)

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {
        "status": "pending",
        "file_name": file.filename,
        "started_at": datetime.utcnow().isoformat() + "Z",
        "progress": 0,
        "total_errors": 0,
        "processed_errors": 0,
        "llm_summary": [],
        "summary": None,
        "error": None,
    }

    asyncio.create_task(_process_job(job_id, file_path))
    # IMPORTANT: return JSON (job_id), not a template
    return {"job_id": job_id, "file_name": file.filename}

@app.get("/summary/{job_id}")
async def get_summary(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JSONResponse({
        "status": job["status"],
        "progress": job["progress"],
        "file_name": job["file_name"],
        "total_errors": job["total_errors"],
        "processed_errors": job["processed_errors"],
        "partial_llm_summary": job["llm_summary"],
        "error": job["error"],
        "is_complete": job["status"] == "completed",
    })

# background worker unchanged (summarize incrementally)
async def _process_job(job_id: str, file_path: str):
    job = JOBS[job_id]
    try:
        job["status"] = "running"

        entries: List[dict] = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        summary = analyze_logs(entries)
        job["summary"] = summary

        errors = summary.get("errors", []) or []
        total = len(errors)
        job["total_errors"] = total

        if total == 0:
            job["progress"] = 100
            job["status"] = "completed"
            return

        job["llm_summary"] = []
        for idx, err in enumerate(errors, start=1):
            err_obj = err if isinstance(err, dict) else {"message": err}
            partial = summarize_each_error([err_obj])  # returns [dict]
            job["llm_summary"].append(partial[0])

            job["processed_errors"] = idx
            job["progress"] = int(idx * 100 / total)

            await asyncio.sleep(0)

        job["status"] = "completed"
        job["progress"] = 100

    except Exception as e:
        job["status"] = "failed"
        job["error"] = str(e)
        job["progress"] = 100
