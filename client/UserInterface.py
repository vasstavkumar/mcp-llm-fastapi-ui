import streamlit as st
import asyncio
import os
from typing import Tuple, Union
import requests
from google import genai
from google.genai import types
from google.genai.types import Tool, FunctionDeclaration
from dotenv import load_dotenv
from llm_handling import handle_gorq_followup, handle_llama_followup, handle_openai_followup

load_dotenv()

class FastAPIClient:
    def __init__(self):
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("Gemini API key not found!")
        self.genai_client = genai.Client(api_key=gemini_api_key)

        self.fastapi_url = os.getenv("FASTAPI_SERVER_URL", "http://fastapi:5002")

        self.function_declarations = [
            Tool(function_declarations=[
                FunctionDeclaration(
                    name="postgres_data",
                    description="Execute a SQL query on the Postgres database",
                    parameters={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                )
            ]),
            Tool(function_declarations=[
                FunctionDeclaration(
                    name="retrieve_tickets",
                    description="Fetch tickets or entries from a Notion database",
                    parameters={
                        "type": "object",
                        "properties": {
                            "database_id": {"type": "string"}
                        },
                        "required": ["database_id"]
                    }
                )
            ])
        ]

    async def process_query(self, query: str, llm_choice: str, chat_history: list) -> Union[str, str, list]:
        user_prompt_content = types.Content(role="user", parts=[{"text": query}])

        full_conversation = chat_history + [user_prompt_content]

        response = self.genai_client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=full_conversation,
            config=types.GenerateContentConfig(tools=self.function_declarations)
        )

        tool_info = ""
        final_text = []

        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    tool_name = part.function_call.name
                    tool_args = part.function_call.args
                    tool_info = f"[Requested tool call: {tool_name} with args {tool_args}]"

                    tool_result = self.call_fastapi_tool(tool_name, tool_args)
                    # config=types.GenerateContentConfig(tools=self.function_declarations)
                    # tool_response = types.Part.from_function_response(
                    #     name=tool_name,
                    #     response={
                    #         "status": "success",
                    #         "data": tool_result
                    #     }
                    # )
                    # contents=[user_prompt_content, types.Content(role="model", parts=[part]), types.Content(role="tool", parts=[tool_response])],


                    final = self.call_llm_handler(llm_choice, tool_result, user_prompt_content)
                    final_text.append(final)

                    # followup_response = self.genai_client.models.generate_content(
                    #     model="gemini-2.0-flash-001",
                    #     config=types.GenerateContentConfig(tools=self.function_declarations)
                    # )

                    # final_text.append(followup_response.candidates[0].content.parts[0].text)
                else:
                    final_text.append(part.text)

        assistant_reply = types.Content(role="model", parts=[{"text": "\n".join(final_text)}])
        updated_history = full_conversation + [assistant_reply]
        return tool_info, "\n".join(final_text), updated_history
    
    def call_llm_handler(self, llm_choice, tool_result, user_prompt_content):

        if llm_choice == "Groq":
            return handle_gorq_followup(tool_result, user_prompt_content)
        elif llm_choice == "LLaMA":
            return handle_llama_followup(tool_result, user_prompt_content)
        elif llm_choice == "OpenAI":
            return handle_openai_followup(tool_result, user_prompt_content)
        else:
            return f"No handler found for {self.llm_choice}."

    def call_fastapi_tool(self, tool_name: str, tool_args: dict):
        try:
            if tool_name == "postgres_data":
                url = f"{self.fastapi_url}/fastapi-postgres"
            elif tool_name == "retrieve_tickets":
                url = f"{self.fastapi_url}/fastapi-notion"
            else:
                return {"error": f"Unknown tool: {tool_name}"}

            response = requests.post(url, json=tool_args)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Streamlit UI
st.title("UI + FastAPI + MCPServer")

llm_choice = st.sidebar.selectbox(
    "Choose an LLM to process your query:",
    ("Groq", "LLaMA", "OpenAI")
)

if "history" not in st.session_state:
    st.session_state.history = []

if "chat_contents" not in st.session_state:
    st.session_state.chat_contents = []

user_query = st.text_input("Ask a question:", placeholder="e.g. retrieve all the tickets related to bugs, here is the database_id", key="user_input")

if st.button("Submit"):
    if user_query:
        with st.spinner("Thinking..."):
            client = FastAPIClient()
            tool_info, answer, updated_chat_history = asyncio.run(client.process_query(user_query, llm_choice, st.session_state.chat_contents))
            st.session_state.history.append((user_query, tool_info, answer))
            st.session_state.chat_contents = updated_chat_history

if st.sidebar.button("Reset Chat"):
    st.session_state.history = []
    st.session_state.chat_contents = []

# Display chat history
for query, tool_call, reply in reversed(st.session_state.history):
    st.markdown(f"**Query:** {query}")
    st.markdown(f"`{tool_call}`")
    st.markdown(f"**Response:**\n{reply}")
    st.markdown("---")
