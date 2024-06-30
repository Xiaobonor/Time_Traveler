# app/utils/openai/openai_assistant.py
import os
import time

import json_repair
from app import openai


class OpenAIAssistant:
    def __init__(self, assistant_id, model="gpt-4o"):
        self.assistant_id = assistant_id
        self.model = model

