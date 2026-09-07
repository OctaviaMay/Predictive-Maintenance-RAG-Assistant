FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# Initialize the Postgres schema (idempotent - CREATE TABLE IF NOT EXISTS)
# then start the app, so `docker compose up` is the only step needed.
CMD ["sh", "-c", "python -c 'from src.database import create_conversation_db; create_conversation_db()' && streamlit run app/app.py --server.port=8501 --server.address=0.0.0.0"]
