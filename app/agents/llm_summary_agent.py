# agents/llm_summary_agent.py
import json
from typing import List, Union, Dict
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Switch model here if you want (e.g., "phi3")
LLM_MODEL = "phi3"

# Single global LLM/chain reused across calls (faster)
_llm = Ollama(model=LLM_MODEL, temperature=0.2, num_predict=512)
_prompt = PromptTemplate(
    input_variables=["error_text"],
    template=(
        "You are a log analysis assistant. Analyze the following log entry and produce a JSON object with keys:\n"
        '  "error_code" (string or null),\n'
        '  "error_name" (string),\n'
        '  "description" (string),\n'
        '  "time" (ISO 8601 string or null),\n'
        '  "possible_cause" (string).\n\n'
        "Log Entry:\n{error_text}\n"
    ),
)
_chain = LLMChain(llm=_llm, prompt=_prompt)

def _to_error_text(err: Union[str, Dict]) -> str:
    """Accepts either a raw string or a dict-like error and formats a stable text."""
    if isinstance(err, str):
        return err
    # Dict case — pick common fields if present
    fields = {
        "time": err.get("time"),
        "level": err.get("level"),
        "message": err.get("message"),
        "operationName": err.get("operationName"),
        "correlationId": err.get("correlationId"),
        "category": err.get("category"),
        "resourceId": err.get("resourceId"),
    }
    # compact JSON to keep tokens down
    return json.dumps({k: v for k, v in fields.items() if v is not None})

def summarize_single_error(err: Union[str, Dict]) -> Dict:
    """Summarize one error entry; always returns a dict."""
    try:
        result = _chain.run({"error_text": _to_error_text(err)})

        # Try to parse JSON; if the model returns text, wrap it.
        try:
            parsed = json.loads(result)
            # Normalize keys
            return {
                "error_code": parsed.get("error_code"),
                "error_name": parsed.get("error_name") or parsed.get("title") or "N/A",
                "description": parsed.get("description") or parsed.get("summary") or "",
                "time": parsed.get("time"),
                "possible_cause": parsed.get("possible_cause") or parsed.get("root_cause") or "",
            }
        except json.JSONDecodeError:
            return {
                "error_code": None,
                "error_name": "Summary",
                "description": result.strip(),
                "time": None,
                "possible_cause": "",
            }
    except Exception as e:
        return {
            "error_code": None,
            "error_name": "LLM Error",
            "description": str(e),
            "time": None,
            "possible_cause": "",
        }

def summarize_each_error(error_list: List[Union[str, Dict]]) -> List[Dict]:
    """Backwards-compatible batch wrapper."""
    return [summarize_single_error(e) for e in error_list]
