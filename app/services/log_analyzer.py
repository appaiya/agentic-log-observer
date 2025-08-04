from typing import List
from datetime import datetime
from dateutil import parser

def analyze_logs(logs: List[dict]) -> dict:
    summary = {
        "total_logs": len(logs),
        "errors": [],
        "warnings": [],
        "info_count": 0
    }

    current_error_block = []
    in_error = False
    previous_time = None

    for log in logs:
        time_str = log.get("time", "")
        timestamp = parser.isoparse(time_str) if time_str else None

        message = log.get("properties", {}).get("message", "").strip()

        level = (
            log.get("level")
            or log.get("properties", {}).get("level")
            or ""
        ).lower()

        is_error_by_content = any(
            err in message.lower()
            for err in ["exception", "traceback", "unhandled", "axioserror"]
        )

        if level == "error" or is_error_by_content:
            if in_error and previous_time and timestamp and abs((timestamp - previous_time).total_seconds()) <= 2:
                current_error_block.append(message)
            else:
                if current_error_block:
                    summary["errors"].append("\n".join(current_error_block))
                current_error_block = [message]
            in_error = True
            previous_time = timestamp

        else:
            if in_error and current_error_block:
                summary["errors"].append("\n".join(current_error_block))
                current_error_block = []
            in_error = False

            if level == "warning" or "warning" in message.lower():
                summary["warnings"].append(message)

            elif level in ["info", "information", "informational"]:
                summary["info_count"] += 1

    # If error block still open at end
    if current_error_block:
        summary["errors"].append("\n".join(current_error_block))

    return summary