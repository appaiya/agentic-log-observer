from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = Ollama(model="phi3")

error_prompt = PromptTemplate(
    input_variables=["error_text"],
    template="""
You are a helpful log analysis assistant.

Given the following application error log, extract and summarize the key debugging details.

--------------------
{error_text}
--------------------

Return a JSON object with the following fields:
- error_title: Short title for the error (e.g., NullReferenceException, TimeoutError)
- error_code: Extract any error code (e.g., 400, ENOENT, etc.), if found
- description: A readable summary of what this error means
- stack_info: File, function, or line where the error occurred (if any)
- probable_cause: Likely root cause of this issue

Respond in pure JSON format only. Do not include any extra explanation.
"""
)

error_chain = LLMChain(llm=llm, prompt=error_prompt)

def summarize_each_error(error_list: list) -> list:
    structured_errors = []
    for idx, error in enumerate(error_list):
        try:
            print(f"Summarizing error #{idx + 1}...")
            result = error_chain.run({"error_text": error})
            structured_errors.append(result)
        except Exception as e:
            structured_errors.append({
                "error": f"Failed to summarize error #{idx + 1}",
                "reason": str(e),
                "raw_error_text": error
            })
    return structured_errors
