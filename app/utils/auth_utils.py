# app/utils/auth_utils.py
import os

from flask import session, redirect, url_for, flash, request
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
            # noinspection PyTypeChecker
            # flash({"title": "授權失敗", "content": "您尚未登入，請先登入後再執行此操作。"}, "popup_error")
            return redirect_to_login()
            # return redirect(url_for('index.home'))

        # Reset the session expiry time on each activity
        session.permanent = True

        return f(*args, **kwargs)

    return decorated_function
