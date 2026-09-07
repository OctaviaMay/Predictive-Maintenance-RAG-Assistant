
from src.ingest import load_machine_data, build_index
from src.metrics import RAGWithMetrics
from openai import OpenAI

# From rag_evaluation notebook, approach A is the winner, so we used it's config
# Get winning approach A config from rag_answer_generation
instruction1 = '''
You are a predictive maintenance assistant for industrial equipment.
Answer the question using ONLY the context below. If the context doesn't
contain enough information, say so rather than guessing.
'''
ptemplate1 = '''
QUESTION: {question}

CONTEXT:
{context}

Give a clear, structured answer: what's happening, why (cite the relevant
mechanism from the context), and recommended action.
'''.strip()

model1 = 'gpt-5.4-mini'


def create_assistant():
    documents = load_machine_data()
    index = build_index(documents)

    assistant = RAGWithMetrics(
        index=index,
        llm_client=OpenAI(),
        instructions=instruction1,
        prompt_template=ptemplate1,
        model = model1
    )
    assistant.section = None
    return assistant