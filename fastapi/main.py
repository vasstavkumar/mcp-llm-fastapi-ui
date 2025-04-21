from fastapi import FastAPI
from pydantic import BaseModel
import requests
import uvicorn

app = FastAPI()

base_url = "http://mcpserver:8002"

class PostgresInput(BaseModel):
    query: str

class NotionInput(BaseModel):
    database_id: str

@app.post("/fastapi-postgres")
def fastapipost(data: PostgresInput):
    url = f"{base_url}/postgres_data"
    response = requests.post(url, json=data.dict())
    return response.json()

@app.post("/fastapi-notion")
def fastapinotion(data: NotionInput):
    url = f"{base_url}/notion_data"
    response = requests.post(url, json=data.dict())
    return response.json()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)
