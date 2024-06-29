import os
import requests
from functools import wraps
from flask import request, jsonify


def verify_turnstile(response_token):
    secret_key = os.getenv("TURNSTILE_SECRET_KEY")
    verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
    payload = {
        'secret': secret_key,
        'response': response_token
    }
    response = requests.post(verify_url, data=payload)
    return response.json()


def turnstile_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.json
        turnstile_response = data.get('cf-turnstile-response')

        if not turnstile_response:
            return jsonify(success=False, message="Turnstile response is required"), 400

        turnstile_verification = verify_turnstile(turnstile_response)
        if not turnstile_verification.get('success'):
            return jsonify(success=False, message="Turnstile verification failed"), 400

        return f(*args, **kwargs)

    return decorated_function
