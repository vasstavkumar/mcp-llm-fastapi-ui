from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from handlers import register_handlers
import requests
import os
import psycopg2 as pg
import asyncio
from pydantic import BaseModel
import uvicorn

load_dotenv()

app = FastAPI()

class postgres_QueryInput(BaseModel):
    query: str

class notion_QueryInput(BaseModel):
    database_id: str

mcp = FastMCP("postgres-notion-server")
register_handlers(mcp)

notion_base_url = "https://api.notion.com/v1/databases/{DATABASE_ID}/query"

headers = {
    "Authorization": f"Bearer {os.getenv('notion_secret')}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# username = os.getenv("POSTGRES_USER")
# # host = os.getenv("host")
# database = os.getenv("POSTGRES_DB")
# password = os.getenv("POSTGRES_PASSWORD")

@mcp.tool()
def retrieve_tickets(database_id: str):
    url = notion_base_url.format(DATABASE_ID=database_id)
    body = {}
    try:
        response = requests.post(url, headers=headers, json=body)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@mcp.tool()
def postgres_data(query: str):
    """
        Tool for answering questions about employees from a PostgreSQL database.

        Use this tool when the user asks anything related to employees, such as:
        - Names, emails, or contact information
        - Department-specific queries
        - Salaries or compensation details
        - Hiring dates or durations
        - Any filter or search based on employee data

        Args:
            query (str): A SQL SELECT query to retrieve employee information from the database.

        Returns:
            str: A human-readable result containing the query response from the employees table.
    """
    try:
        conn = pg.connect(
            port=5432,
            host="postgres",
            database="mydb",
            password="postgres",
            user="postgres"
        )
        cursor = conn.cursor()
        cursor.execute(query=query)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"status": "success", "data": results}

    except pg.Error as e:
        return {"error": str(e)}

@mcp.prompt()
def query_prompt(question: str):
    return f"Based on the question give the PostgreSQL query. Use the MCP resource for the structure of the database.\n\nQuestion: {question}"

@app.post("/postgres_data")
async def postgres(query_input: postgres_QueryInput):
    query = query_input.query
    results = postgres_data(query)
    return {"status": "success", "data": results}

@app.post("/notion_data")
async def notion(database: notion_QueryInput):
    database_id = database.database_id
    results = retrieve_tickets(database_id)
    return {"status": "success", "data": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)