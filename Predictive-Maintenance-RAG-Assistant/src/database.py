import os
import psycopg
from dataclasses import dataclass, field
from tqdm.auto import tqdm
from datetime import datetime
from src.metrics import LLMCallRecord
import logging
logger = logging.getLogger(__name__)

DB_TIMEZONE = datetime.now().astimezone().tzinfo
# logger.info(f"Using timezone: {DB_TIMEZONE}")



@dataclass
class Stats:
    total: int
    avg_response_time: float
    total_cost: float
    avg_tokens: float


def row_to_record(row):
    return LLMCallRecord(
        model=row[4],
        prompt=row[6],
        instructions=row[5],
        answer=row[2],
        prompt_tokens=row[7],
        completion_tokens=row[8],
        total_tokens=row[9],
        response_time=row[10],
        cost=row[11],
        question=row[1],
        timestamp=row[12],
    )


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port = 5432,
        dbname=os.getenv("POSTGRES_DB", "pm_assistant"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "pswd"),
    )


def create_conversation_db(drop=False):
    """Create the conversations/feedback tables if they don't already exist.

    Raises on failure so a broken database stops startup instead of
    failing silently on the first user question.
    """
  
    logger.info("Initialising PostgreSQL schema...")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if drop:
                cur.execute("DROP TABLE IF EXISTS feedback CASCADE")
                cur.execute("DROP TABLE IF EXISTS conversations CASCADE")
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    section TEXT NOT NULL,
                    model TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    response_time FLOAT NOT NULL,
                    cost FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
                    source TEXT NOT NULL,
                    relevance TEXT,
                    explanation TEXT,
                    score INTEGER,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            
            cur.execute("""
                ALTER TABLE feedback
                    ADD COLUMN IF NOT EXISTS model TEXT,
                    ADD COLUMN IF NOT EXISTS prompt_tokens INTEGER,
                    ADD COLUMN IF NOT EXISTS completion_tokens INTEGER,
                    ADD COLUMN IF NOT EXISTS total_tokens INTEGER,
                    ADD COLUMN IF NOT EXISTS response_time FLOAT,
                    ADD COLUMN IF NOT EXISTS cost FLOAT
            """)

    logger.info("Schema ready.")

    

def save_conversation(answer_record, question, section):
    timestamp = datetime.now(DB_TIMEZONE)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (
                    question, answer, section, model, instructions, prompt,
                    prompt_tokens, completion_tokens, total_tokens,
                    response_time, cost, timestamp
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
                """,
                (
                    question,
                    answer_record.answer,
                    section,
                    answer_record.model,
                    answer_record.instructions,
                    answer_record.prompt,
                    answer_record.prompt_tokens,
                    answer_record.completion_tokens,
                    answer_record.total_tokens,
                    answer_record.response_time,
                    answer_record.cost,
                    timestamp,
                ),
            )
            conversation_id = cur.fetchone()[0]
    
    return conversation_id


def save_feedback(conversation_id, source, relevance=None,
                  explanation=None, score=None, judge= None):

    judge = judge or {}
    timestamp = datetime.now(DB_TIMEZONE)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO feedback (
                    conversation_id, source, relevance,explanation, score, 
                    model, prompt_tokens, completion_tokens, total_tokens,
                    response_time, cost,timestamp
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (conversation_id, source, relevance, explanation, score,
                 judge.get("model"), judge.get("prompt_tokens"), judge.get("completion_tokens"),judge.get("total_tokens"),
                judge.get("response_time"), judge.get("cost"),
                 timestamp),
            )
   

def get_conversations(limit=10):
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, question, answer, section, model,
                       instructions, prompt,
                       prompt_tokens, completion_tokens, total_tokens,
                       response_time, cost, timestamp
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()

    return [row_to_record(row) for row in rows]


def get_statistic():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*),
                    AVG(c.response_time),
                    SUM(c.cost) + COALESCE((SELECT SUM(cost) FROM feedback WHERE source = 'judge'), 0),
                    AVG(c.total_tokens)
                FROM conversations c
            """)
            row = cur.fetchone()

    return Stats(
        total=row[0] or 0,
        avg_response_time=row[1] or 0.0,
        total_cost=row[2] or 0.0,
        avg_tokens=row[3] or 0.0,
    )
