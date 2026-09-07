from pathlib import Path
from dotenv import load_dotenv
from minsearch import Index
from datetime import datetime
import psycopg
from tqdm.auto import tqdm
import os
import json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MACHINE_DATA_LOCAL_PATH = PROJECT_ROOT / "data" / "knowledge_base.json"

def load_machine_data():
    load_dotenv()
    print(f"Loading knowledge base from json file: {MACHINE_DATA_LOCAL_PATH}")
    with open(MACHINE_DATA_LOCAL_PATH) as mdata_file:
        documents = json.load(mdata_file)
    print(f"Loaded machine data:{len(documents)}")

    return documents
    
def build_index(documents):
    index = Index(
        text_fields=['question','section','answer'],
        keyword_fields=['section']
    )
    index.fit(documents)

    return index


