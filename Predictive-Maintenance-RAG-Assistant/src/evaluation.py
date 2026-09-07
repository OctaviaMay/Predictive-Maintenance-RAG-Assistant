
import sys
from pathlib import Path
import time
import json
from tqdm.auto import tqdm

from src.rag_helper import RAGBase
from src.search import vector_search

def get_llm_response(client, instructions,user_prompt,output_type, model):
    messages =[
        {'role':'developer','content':instructions},
        {'role':'user','content':user_prompt}
    ]

    response = client.responses.parse(
        model=model,
        input = messages,
        text_format = output_type
    )

    return response.output_parsed, response.usage

def get_llm_response_retry(client, instructions,user_prompt,output_type, model, max_retries = 3):
    for attempt in range(max_retries):
        try:
            return get_llm_response(client, instructions,user_prompt,output_type, model)
        except Exception:
            if attempt == max_retries - 1:
                raise 
            time.sleep(2 ** attempt)


def calculate_price(usage):
    input_price_per_million = 0.75
    output_price_per_million = 4.50

    input_cost = (usage.input_tokens / 1_000_000) * input_price_per_million
    output_cost = (usage.output_tokens / 1_000_000) * output_price_per_million
    total_cost = input_cost + output_cost

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
    }

def calculate_total_price(usages):
    total_cost = 0.0

    for u in usages:
        cost = calculate_price(u)
        total_cost = total_cost + cost['total_cost']

    return total_cost
    

def map_progress(pool, seq, f):
    results = []

    with tqdm(total=len(seq)) as progress:
        futures = []

        for el in seq:
            future = pool.submit(f, el)
            future.add_done_callback(lambda p: progress.update())
            futures.append(future)

        for future in futures:
            result = future.result()
            results.append(result)

    return results


 

class RAGWithUsage(RAGBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usages = []
        self.last_usage = None
        self.section = None

    def reset_usage(self):
        self.usages = []
        self.last_usage = None

   
    def search(self, query):
        return vector_search(query)

    def llm(self, prompt):
        input_messages = [
            {"role": "developer", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        self.last_usage = response.usage
        self.usages.append(response.usage)

        return response.output_text

    def total_cost(self):
        return calculate_total_price(self.usages)




def evaluate_rag_answer(aqa_judge_prompt,record,openai_client,aqa_judge_instructions,AnswerEvaluation,model):
    prompt = aqa_judge_prompt.format(
        question = record['question'],
        answer_orig = record['original_answer'],
        answer_llm = record['llm_answer']
        )

    eval_result, usage =get_llm_response_retry(openai_client,aqa_judge_instructions,prompt,AnswerEvaluation,model)

    return eval_result, usage

