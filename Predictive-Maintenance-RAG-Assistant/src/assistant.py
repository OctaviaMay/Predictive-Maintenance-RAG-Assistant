
from src.ingest import load_machine_data, build_index
from src.metrics import RAGWithMetrics
from openai import OpenAI
from src.prompt import ANSWER_MODEL, INSTRUCTIONS, PROMPT_TEMPLATE
from src.search import get_retriever


def create_assistant():
   
    assistant = RAGWithMetrics(
        index= get_retriever(),
        llm_client=OpenAI(),
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        model = ANSWER_MODEL
    )
    
    return assistant