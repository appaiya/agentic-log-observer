from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import json

from app.services.log_analyzer import analyze_logs
from app.agents.llm_summary_agent import summarize_each_error

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload_log(request: Request, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    log_data = []
    for line in contents.decode("utf-8").splitlines():
        try:
            log_data.append(json.loads(line.strip()))
        except json.JSONDecodeError:
            continue

    summary = analyze_logs(log_data)
    llm_summary = summarize_each_error(summary["errors"])

    return templates.TemplateResponse("result.html", {
        "request": request,
        "summary": summary,
        "llm_summary": llm_summary,
        "file_name": file.filename
    })