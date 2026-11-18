

from src.search import vector_search
from src.prompt import ANSWER_MODEL, INSTRUCTIONS, PROMPT_TEMPLATE

class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        instructions,
        prompt_template,
        model
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.model = model
        self.last_context = None # context used for the most recent answer

   
    def search(self, query, num_results=5):
        boost_dict = {'question': 3.0, 'section': 0.5}
        filter_dict = {'section': self.section}

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict,
            filter_dict=filter_dict
        )
    
    def build_context(self,search_results):
        lines = []

        for doc in search_results:
            lines.append(doc['section'])
            lines.append('Q: ' + doc['question'])
            lines.append('A: ' + doc['answer'])
            lines.append('')

        return '\n'.join(lines).strip()
        
    def build_prompt(self,query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )

    def llm(self,prompt):
        input_messages = [
            {'role': 'developer', 'content': self.instructions},
            {'role': 'user', 'content': prompt}
        ]

        response = self.llm_client.responses.create(
            model = self.model,
            input=input_messages
        )

        return response.output_text

    def rag(self,query):
        search_results = self.search(query)
        self.last_context = self.build_context(search_results)
        prompt = self.prompt_template.format(question=query,context=self.last_context)
        answer = self.llm(prompt)
        return answer