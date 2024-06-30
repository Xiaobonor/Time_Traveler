# app/utils/openai/openai_chat.py
from app import openai


async def generate_text_with_messages(messages, model="gpt-4o"):
    completion = openai.chat.create(
        model=model,
        messages=messages
    )
    message = completion.choices[0].message
    usage = completion.usage.total_tokens
    return message.content, usage


async def generate_text(system_prompt, user_prompt, model="gpt-4o"):
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
