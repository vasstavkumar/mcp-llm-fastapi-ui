from typing import List, Dict, Any
from google import genai
import google.genai as genai, types
import os
from groq import Groq
from openai import OpenAI
from google.genai import Client


# def handle_gemini_followup(contents, config):
#     genai_client= Client(
#         api_key=os.getenv("GEMINI_API_KEY"),
#     )

#     followup_response =  genai_client.models.generate_content(
#         model="gemini-2.0-flash-001",
#         contents= contents,
#         config=config
#     )
    
#     return followup_response.candidates[0].content.parts[0].text

def handle_gorq_followup(tool_result, user_prompt_content):
    groq_client = Groq(
        api_key= os.getenv("GROQ_API_KEY")
    )
    tool_result = str(tool_result)
    user_prompt_content = str(user_prompt_content)
    chat_completion = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant. Use the following information provided by the user to answer questions accurately: \n\n" + tool_result
            },
            {
                "role": "user",
                "content": "Based on the provided information, " + user_prompt_content
            }
        ]
    )
    return chat_completion.choices[0].message.content


def handle_openai_followup(tool_result, user_prompt_content):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    chat_completion = client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt= [
            {
                "role": "system",
                "content": "You are an AI assistant. Use the following information provided by the user to answer questions accurately: \n\n" + tool_result
            },
            {
                "role": "user",
                "content": "Based on the provided information, " + user_prompt_content
            }
        ]
    )
    return chat_completion.choices[0].message.content


def handle_llama_followup(tool_result, user_prompt_content):
    groq_client = Groq(
        api_key= os.getenv("GROQ_API_KEY")
    )
    tool_result = str(tool_result)
    user_prompt_content = str(user_prompt_content)
    chat_completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages = [
            {
                "role": "system",
                "content": "You are an AI assistant. Use the following information provided by the user to answer questions accurately: \n\n" + tool_result
            },
            {
                "role": "user",
                "content": "Based on the provided information, " + user_prompt_content
            }
        ]
    )
    return chat_completion.choices[0].message.content
