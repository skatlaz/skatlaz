#main.py

from your_module import llm, ingest_file

def run_ai(user_id, prompt):
    return llm(user_id, prompt)

def upload(user_id, path):
    return ingest_file(user_id, path)
