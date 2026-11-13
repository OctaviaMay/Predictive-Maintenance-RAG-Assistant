from src.prompt import INSTRUCTIONS, PROMPT_TEMPLATE
from src.rag_helper import RAGBase


def test_prompt_contains_question_and_context():
    rag = RAGBase(index=None, llm_client=None, instructions=INSTRUCTIONS,
                  prompt_template=PROMPT_TEMPLATE, model="x")
    docs = [{"section": "Power Failure", "question": "Q1?", "answer": "A1."}]
    prompt = rag.build_prompt("Why did it fail?", docs)
    assert "Why did it fail?" in prompt
    assert "A1." in prompt