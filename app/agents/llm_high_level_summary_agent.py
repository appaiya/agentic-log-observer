
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = Ollama(model="phi3")

prompt = PromptTemplate(
    input_variables=["log_stats"],
    template="""
You are a log analysis assistant. Here's a structured summary of a system log file:

{log_stats}

Based on the above data, write a clear and concise report:
- What kind of errors are present?
- How frequent are the issues?
- What are the top 2–3 possible causes?
- Mention any trends, warnings, or anomalies
- Suggest action items or areas to investigate

The output should be readable by a technical lead or SRE.
"""
)

log_summary_chain = LLMChain(llm=llm, prompt=prompt)

def top_level_summary(log_stats: dict) -> str:
    response = log_summary_chain.run(log_stats=str(log_stats))
    return response