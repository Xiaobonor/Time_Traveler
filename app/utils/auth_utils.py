# app/utils/auth_utils.py
import os

from flask import session, redirect, request
from functools import wraps


def login_required(f):
    """
    Decorator to check if the user is logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        def redirect_to_login():
            sso_login_url = os.getenv('HOST_DOMAIN') + '/auth/login'
            next_url = request.url
            return redirect(f"{sso_login_url}?next={next_url}")

        if 'user_info' not in session:
            return redirect_to_login()

        # Reset the session expiry time on each activity
        session.permanent = True

        return f(*args, **kwargs)

    return decorated_function
