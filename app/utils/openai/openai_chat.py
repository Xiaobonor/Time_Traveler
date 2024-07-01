# app/utils/openai/openai_chat.py
from app import openai


async def generate_text_with_messages(messages, model="gpt4o"):
    """
    Generate text using custom messages
    :param messages: should be a list of dictionaries with keys "role" and "content"
    :param model: model to use
    :return: generated text and usage
    """
    completion = openai.chat.create(
        model=model,
        messages=messages
    )
    message = completion.choices[0].message
    usage = completion.usage.total_tokens
    return message.content, usage


async def generate_text(system_prompt, user_prompt, model="gpt4o"):
    """
    Generate text using system and user prompts
    This is a one-time use function, use generate_text_with_messages for multiple messages
    :param system_prompt: system prompt for message
    :param user_prompt: user input
    :param model: model to use
    :return: generated text and usage
    """
    completion = openai.chat.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    message = completion.choices[0].message
    usage = completion.usage.total_tokens
    return message.content, usage
