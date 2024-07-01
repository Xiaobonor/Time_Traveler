# app/utils/openai/assistant_manager.py
# This file is a modified version of the assistant_manager.py from the repository at
# https://github.com/shamspias/openai-assistent-python/tree/main. This version has been
# modified by Xiaobonor.
from typing import Optional
from app import openai


async def list_assistants():
    response = await openai.beta.assistants.list()
    return {assistant.name: assistant.id for assistant in response.data}


async def retrieve_assistant(assistant_id: str):
    return await openai.beta.assistants.retrieve(assistant_id)


async def create_assistant(name: str, instructions: str, tools: list, model: str):
    return await openai.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=tools,
        model=model
    )


async def update_assistant(assistant_id: str, name: Optional[str] = None, description: Optional[str] = None,
                           instructions: Optional[str] = None, tools: Optional[list] = None):
    update_fields = {}
    if name is not None:
        update_fields['name'] = name
    if description is not None:
        update_fields['description'] = description
    if instructions is not None:
        update_fields['instructions'] = instructions
    if tools is not None:
        update_fields['tools'] = tools
    return await openai.beta.assistants.update(assistant_id, **update_fields)


async def delete_assistant(assistant_id: str):
    return await openai.beta.assistants.delete(assistant_id)


async def create_assistant_file(assistant_id: str, file_id: str):
    return await openai.beta.assistants.files.create(assistant_id=assistant_id, file_id=file_id)


async def delete_assistant_file(assistant_id: str, file_id: str):
    return await openai.beta.assistants.files.delete(assistant_id, file_id)


async def list_assistant_files(assistant_id: str):
    return await openai.beta.assistants.files.list(assistant_id)


async def get_assistant_id_by_name(name: str):
    """
    Get the ID of an assistant by its name.

    Args:
        name (str): The name of the assistant.

    Returns:
        str: The ID of the assistant if found, otherwise None.
    """
    assistants = await list_assistants()
    return assistants.get(name)