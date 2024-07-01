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


async def get_runs_by_thread(thread_id: str):
    return await openai.beta.threads.runs.list(thread_id=thread_id)


async def submit_tool_outputs_and_poll(thread_id: str, run_id: str, tool_outputs: list):
    return await openai.beta.threads.runs.submit_tool_outputs_and_poll(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs
    )