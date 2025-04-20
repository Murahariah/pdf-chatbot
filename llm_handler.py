from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from cachetools import TTLCache
import sqlite3
import json

# --- LLM Setup ---
try:
    llm = ChatOllama(model="mistral")
except Exception as e:
    print(f"Error initializing LLM: {e}")
    llm = None

output_parser = StrOutputParser()
cache = TTLCache(maxsize=100, ttl=3600)  # Cache 100 responses for 1 hour

# --- Prompt Template ---
rag_prompt_template = """
You are a customer support assistant. Answer the user's question using only the provided context, rephrasing raw data into concise, conversational language. Use conversation history for follow-ups if relevant. If no answer is found in the context, politely state that the information is not available and suggest providing more details.

Conversation History:
{history}

Current Context:
{context}

User Query:
{query}

Response:
"""

rag_prompt = ChatPromptTemplate.from_template(rag_prompt_template)

# --- Langchain Chain ---
if llm:
    rag_chain = rag_prompt | llm | output_parser
else:
    rag_chain = None

# --- Database Query Function ---
def query_database(db_path, query):
    """Query SQLite database for relevant text, images, or tables."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        context = []
        query_words = query.lower().split()  # Split query into words for better matching
        
        # Search texts
        for word in query_words:
            query_like = f"%{word}%"
            cursor.execute("SELECT page_number, content FROM texts WHERE content LIKE ?", (query_like,))
            texts = cursor.fetchall()
            for page, content in texts:
                context.append({"type": "text", "page": page, "content": content[:500]})  # Limit length
        
        # Search tables
        cursor.execute("SELECT page_number, table_index, content FROM tables")
        tables = cursor.fetchall()
        for page, idx, content in tables:
            try:
                table_data = json.loads(content)
                table_str = "\n".join([",".join(str(cell) if cell is not None else "" for cell in row) for row in table_data])
                if any(word in table_str.lower() for word in query_words):
                    context.append({"type": "table", "page": page, "index": idx, "content": table_str[:500]})
            except Exception as e:
                print(f"Error processing table {idx} on page {page}: {e}")
                continue
        
        # Search images (basic metadata search)
        cursor.execute("SELECT image_name, image_format FROM images")
        images = cursor.fetchall()
        for name, fmt in images:
            if any(word in name.lower() for word in query_words):
                context.append({"type": "image", "name": name, "format": fmt})
        
        conn.close()
        return context
    except Exception as e:
        print(f"Error querying database: {e}")
        return []

# --- Function to get Response ---
def get_rag_response(user_query: str, db_path: str, context_history: list[dict]):
    if not rag_chain:
        return "Error: LLM unavailable.", "LLM initialization failed."
    
    # Query database for context
    retrieved_context = query_database(db_path, user_query)
    
    # Cache key: query + simplified context
    cache_key = f"{user_query}::{str(retrieved_context)[:100]}"
    if cache_key in cache:
        return cache[cache_key], "Data fetched from cache."
    
    history_str = "\n".join([f"Q: {item['query']} A: {item['response']}" for item in context_history[-3:]]) if context_history else "No history."
    context_str = "\n".join([f"{item['type'].upper()} (Page {item['page']}): {item['content']}" if item['type'] != "image" else f"IMAGE: {item['name']}" for item in retrieved_context]) if retrieved_context else "No relevant information found in the database."
    
    status_message = "Data successfully fetched from database." if retrieved_context else "No relevant data found in the database for this query."
    
    try:
        response = rag_chain.invoke({"history": history_str, "context": context_str, "query": user_query})
        cache[cache_key] = response
        return response, status_message
    except Exception as e:
        print(f"Error invoking LLM: {e}")
        return "Sorry, an error occurred while processing your query.", "LLM processing failed."