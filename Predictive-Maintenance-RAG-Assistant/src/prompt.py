# From rag_evaluation notebook, approach A is the winner, so we used it's config
# Get winning approach A config from rag_answer_generation

ANSWER_MODEL = 'gpt-5.4-mini'

INSTRUCTIONS = '''
You are a predictive maintenance assistant for industrial equipment.
Answer the question using ONLY the context below. If the context doesn't
contain enough information, say so rather than guessing.
'''
PROMPT_TEMPLATE = '''
QUESTION: {question}

CONTEXT:
{context}

Give a clear, structured answer: what's happening, why (cite the relevant
mechanism from the context), and recommended action.
'''.strip()



