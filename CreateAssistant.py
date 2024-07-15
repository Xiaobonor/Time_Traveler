# Auto create assistant and get assistant id
# If you don't have all of our assistant, you should run this script to create and get assistants.
# TODO:
import asyncio
import os

from app import create_app
app = create_app()
import openai_assistant as assistant_manager

smart_model = os.getenv("MODEL_SMART_NAME", "gpt4o")

# Travel demand analysis expert(TDAE)
from app.utils.agents.assistant.travel_needs import prompt as TDAE_prompt
TDAE = asyncio.run(assistant_manager.create_assistant(
    name="TDAE",
    instructions=TDAE_prompt,
    tools=[
       {
           "type": "function",
           "function": {
               "name": "web_search_bing",
               "description": "Search the information online for the user's travel needs.",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "query": {
                           "type": "string",
                           "description": "The search query string, must in english.",
                       },
                       "count": {
                           "type": "integer",
                           "description": "The number of search results to return.",
                           "default": 10
                       },
                       "offset": {
                           "type": "integer",
                           "description": "The number of search results to skip.",
                           "default": 0
                       },
                       "web_page": {
                           "type": "boolean",
                           "description": "Whether to include web page results.",
                           "default": True
                       },
                       "image": {
                           "type": "boolean",
                           "description": "Whether to include image results.",
                           "default": False
                       },
                       "news": {
                           "type": "boolean",
                           "description": "Whether to include news results.",
                           "default": False
                       },
                       "video": {
                           "type": "boolean",
                           "description": "Whether to include video results.",
                           "default": False
                       },
                       "fetch_content": {
                           "type": "boolean",
                           "description": "Whether to fetch the content of the web pages.",
                           "default": True
                       },
                       "content_length_limit": {
                           "type": "integer",
                           "description": "The maximum length of the fetched content.",
                           "default": 3000
                       }
                   },
                   "required": ["query"]
               }
           }
       }
    ],
    model=smart_model))
print("Assistant TDAE created successfully!")
print(f"Assistant ID: {TDAE.id}")

# Travel demand analysis expert(TDAE)
from app.utils.agents.assistant.travel_plan import prompt as TPE_prompt
TPE = asyncio.run(assistant_manager.create_assistant(
    name="TPE",
    instructions=TPE_prompt,
    tools=[
       {
           "type": "function",
           "function": {
               "name": "web_search_bing",
               "description": "Search the information online for the user's travel needs.",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "query": {
                           "type": "string",
                           "description": "The search query string, must in english.",
                       },
                       "count": {
                           "type": "integer",
                           "description": "The number of search results to return.",
                           "default": 10
                       },
                       "offset": {
                           "type": "integer",
                           "description": "The number of search results to skip.",
                           "default": 0
                       },
                       "web_page": {
                           "type": "boolean",
                           "description": "Whether to include web page results.",
                           "default": True
                       },
                       "image": {
                           "type": "boolean",
                           "description": "Whether to include image results.",
                           "default": False
                       },
                       "news": {
                           "type": "boolean",
                           "description": "Whether to include news results.",
                           "default": False
                       },
                       "video": {
                           "type": "boolean",
                           "description": "Whether to include video results.",
                           "default": False
                       },
                       "fetch_content": {
                           "type": "boolean",
                           "description": "Whether to fetch the content of the web pages.",
                           "default": True
                       },
                       "content_length_limit": {
                           "type": "integer",
                           "description": "The maximum length of the fetched content.",
                           "default": 3000
                       }
                   },
                   "required": ["query"]
               }
           }
       }
    ],
    model=smart_model))
print("Assistant TPE created successfully!")
print(f"Assistant ID: {TPE.id}")

# Travel demand analysis expert(TDAE)
from app.utils.agents.assistant.travel_items import prompt as TIAE_prompt
TIAE = asyncio.run(assistant_manager.create_assistant(
    name="TIAE",
    instructions=TIAE_prompt,
    tools=[
       {
           "type": "function",
           "function": {
               "name": "web_search_bing",
               "description": "Search the information online for the user's travel needs.",
               "parameters": {
                   "type": "object",
                   "properties": {
                       "query": {
                           "type": "string",
                           "description": "The search query string, must in english.",
                       },
                       "count": {
                           "type": "integer",
                           "description": "The number of search results to return.",
                           "default": 10
                       },
                       "offset": {
                           "type": "integer",
                           "description": "The number of search results to skip.",
                           "default": 0
                       },
                       "web_page": {
                           "type": "boolean",
                           "description": "Whether to include web page results.",
                           "default": True
                       },
                       "image": {
                           "type": "boolean",
                           "description": "Whether to include image results.",
                           "default": False
                       },
                       "news": {
                           "type": "boolean",
                           "description": "Whether to include news results.",
                           "default": False
                       },
                       "video": {
                           "type": "boolean",
                           "description": "Whether to include video results.",
                           "default": False
                       },
                       "fetch_content": {
                           "type": "boolean",
                           "description": "Whether to fetch the content of the web pages.",
                           "default": True
                       },
                       "content_length_limit": {
                           "type": "integer",
                           "description": "The maximum length of the fetched content.",
                           "default": 3000
                       }
                   },
                   "required": ["query"]
               }
           }
       }
    ],
    model=smart_model))
print("Assistant TIAE created successfully!")
print(f"Assistant ID: {TIAE.id}")