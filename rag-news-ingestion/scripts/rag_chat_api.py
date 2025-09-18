# rag_chat_api.py
import sys
from rag_chat import rag_query  # import the RAG function

if len(sys.argv) < 2:
    print("No query provided")
    sys.exit(1)

query = sys.argv[1]
answer = rag_query(query)
print(answer)
