import json
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal
from openai import OpenAI

from src.evaluation import get_llm_response_retry

class RelevanceVerdict(BaseModel):
    relevance:Literal['NON_RELEVANT','PARTIAL_RELEVANT','RELEVANT']
    explanation: str

judge_instructions = """
You are an expert evaluator for a RAG system.
Analyze the relevance of the generated answer to the given question.

Classify the answer as:
- RELEVANT: the answer addresses the question
- PARTLY_RELEVANT: the answer partially addresses the question
- NON_RELEVANT: the answer does not address the question
""".strip()

judge_prompt = """
Question: {question}
Generated Answer: {answer}
""".strip()

def evaluate_relevance(question, answer, client=None):
    if client is None:
        client = OpenAI()

    prompt = judge_prompt.format(
        question = question,
        answer = answer
    )

    result, usage =get_llm_response_retry(client, 
                           judge_instructions,
                           prompt,
                           RelevanceVerdict,'gpt-5.4-mini')

    return result.relevance, result.explanation
    
