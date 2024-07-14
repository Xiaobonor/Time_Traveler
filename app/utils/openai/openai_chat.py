# app/utils/openai/openai_chat.py
import os
from app import openai
default_model = os.getenv("MODEL_CHAT_DEFAULT", "gpt-4o")


async def generate_text_with_messages(messages, model=default_model):
    """
    Generate text using custom messages
    :param messages: should be a list of dictionaries with keys "role" and "content"
    :param model: model to use
    :return: generated text and usage
    """
    completion = await openai.chat.completions.create(
        model=model,
        messages=messages
    )
    message = completion.choices[0].message
    usage = completion.usage.total_tokens
    return message.content, usage


async def generate_text(system_prompt, user_prompt, model=default_model):
    """
    Generate text using system and user prompts
    This is a one-time use function, use generate_text_with_messages for multiple messages
    :param system_prompt: system prompt for message
    :param user_prompt: user input
    :param model: model to use
    :return: generated text and usage
    """
    completion = await openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    message = completion.choices[0].message
    usage = completion.usage.total_tokens
    return message.content, usage


async def generate_text_with_images(system_prompt: str, base64s: list, model=default_model):
    """
    Generate text using images
    :param system_prompt: system prompt for message
    :param base64s: list of image base64 strings
    :param model: model to use
    :return: generated text and usage
    """
    if len(base64s) > 10:
        raise ValueError("A maximum of 10 images is allowed.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": []}
    ]

    for base64 in base64s:
        messages[1]["content"].append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"{base64}"
                }
            }
        )

    completion = await openai.chat.completions.create(
        model=model,
        messages=messages
    )
    message = completion.choices[0].message
    usage = completion.usage.total_tokens
    return message.content, usage
