import json
from agents.llm_summary_agent import summarize_each_error
from agents.llm_high_level_summary_agent import top_level_summary
from fastapi import APIRouter, UploadFile, File
from services.log_analyzer import analyze_logs
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_log(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        log_data = []  
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        log_data.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        if not log_data:
            return { "message": "No valid log entries found in the file" }

        summary = analyze_logs(log_data)
        top_level = top_level_summary(summary)
        # llm_summary = summarize_each_error(summary["errors"])

        return {
            "messgae": "Log analyzed successfully",
            # "summary": summary,
            "top_level": top_level,
            # "llm_summary": llm_summary
        }
    except Exception as e:
        return {
            "message": "Failed to process the file",
            "error": str(e)
        }