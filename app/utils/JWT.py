import os
import time
from functools import wraps

from authlib.jose import jwt
from flask import request, redirect, session, jsonify


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        def redirect_to_sso():
            sso_login_url = os.getenv('HOST_DOMAIN') + '/auth/login'
            next_url = request.url
            return redirect(f"{sso_login_url}?next={next_url}")
        token = request.cookies.get('jwt')
        if not token:
            return redirect_to_sso()

        try:
            data = jwt.decode(token.encode('utf-8'), os.getenv("D_SECRET_KEY"))
            if data['exp'] <= time.time():
                return redirect_to_sso()
            session['user'] = data
        except Exception as e:
            return redirect(f"https://xiaobo.tw/error?msg={str(e)}")

        return f(*args, **kwargs)
    return decorated


def jwt_process(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        def redirect_to_sso():
            sso_login_url = os.getenv('HOST_DOMAIN') + '/auth/login'
            next_url = request.url
            return redirect(f"{sso_login_url}?next={next_url}")

        token = request.cookies.get('jwt')
        print(token)
        if not token:
            print('no token')
            return f(*args, **kwargs)

        if 'user' not in session or session['user'] is None:
            try:
                session['user'] = jwt.decode(token.encode('utf-8'), os.getenv("D_SECRET_KEY"))
            except Exception as e:
                print(f"Error decoding token: {e}")
                return redirect_to_sso()

        if session['user']['exp'] <= time.time():
            print('token expired')
            return redirect_to_sso()

        print(session['user'])
        return f(*args, **kwargs)

    return decorated
