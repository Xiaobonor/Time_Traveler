# app/utils/openai/openai_token_calculation.py
import tiktoken
from flask import session, request, jsonify
from functools import wraps


def get_token_usage(prompt, response_text):
    prompt_tokens = estimate_tokens(prompt)
    response_tokens = estimate_tokens(response_text)
    return prompt_tokens + response_tokens


def estimate_tokens(prompt):
    encoding = tiktoken.encoding_for_model("gpt-4o")
    tokens = encoding.encode(prompt)
    return len(tokens)


def check_token_limit_decorator(system_prompt, additional_tokens=100):
    """
    This decorator checks if the user has enough tokens to generate a response.
    :param system_prompt: System prompt
    :param additional_tokens: You can specify additional tokens to be used
    :return:
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            user_prompt = str(data.get('user_prompt', ''))

            if not user_prompt:
                return jsonify(success=False, message='缺少提示詞內容'), 400

            estimated_tokens = estimate_tokens(system_prompt) + estimate_tokens(user_prompt)
            user_token_limit = session['user_info']['tokens']

            if (estimated_tokens + additional_tokens) > user_token_limit:
                return jsonify(success=False, message='您的token數量不足本次使用'), 400

            return f(*args, **kwargs)

        return decorated_function

    return decorator
