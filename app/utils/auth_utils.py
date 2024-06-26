# app/utils/auth_utils.py
from flask import session, redirect, url_for, flash
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_info' not in session:
            # noinspection PyTypeChecker
            flash({"title": "授權失敗", "content": "您尚未登入，請先登入後再執行此操作。"}, "popup_error")
            return redirect(url_for('index.home'))

        # Reset the session expiry time on each activity
        session.permanent = True

        return f(*args, **kwargs)

    return decorated_function
