# app/utils/openai/thread_manager.py
# This file is a modified version of the thread_manager.py from the repository at
# https://github.com/shamspias/openai-assistent-python/tree/main. This version has been
# modified by Xiaobonor.
import json
import os
from typing import Optional
from app import openai


async def list_messages(thread_id: str, limit: int = 20, order: str = 'desc', after: Optional[str] = None,
                        before: Optional[str] = None):
    try:
        return await openai.beta.threads.messages.list(thread_id=thread_id, limit=limit, order=order, after=after,
                                                       before=before)
    except Exception as e:
        print(f"An error occurred while retrieving messages: {e}")
        return None


async def retrieve_message(thread_id: str, message_id: str):
    return await openai.beta.threads.messages.retrieve(thread_id=thread_id, message_id=message_id)


async def create_thread(messages: Optional[list] = None, metadata: Optional[dict] = None):
    return await openai.beta.threads.create(messages=messages, metadata=metadata)


async def retrieve_thread(thread_id: str):
    return await openai.beta.threads.retrieve(thread_id)


async def modify_thread(thread_id: str, metadata: dict):
    return await openai.beta.threads.modify(thread_id, metadata=metadata)


async def delete_thread(thread_id: str):
    return await openai.beta.threads.delete(thread_id)


async def send_message(thread_id: str, content: str, role: str = "user"):
    return await openai.beta.threads.messages.create(thread_id=thread_id, role=role, content=content)


async def create_run(thread_id: str, assistant_id: str):
    return await openai.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)


async def list_runs(thread_id: str):
    return await openai.beta.threads.runs.list(thread_id=thread_id)


def read_thread_data(filename: str = 'data.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    return {}


def save_thread_data(thread_id: str, filename: str = 'data.json'):
    data = {'thread_id': thread_id}
    with open(filename, 'w') as file:
        json.dump(data, file)
