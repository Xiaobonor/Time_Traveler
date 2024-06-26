# app/routes/auth.py
from flask import Blueprint, redirect, url_for, session, flash
from app import oauth
from app.models.user import User
import os

from app.utils.auth_utils import login_required


auth_bp = Blueprint('auth', __name__)

google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    client_kwargs={'scope': 'openid profile email'}
)


@auth_bp.route('/login')
def login():
    if 'user_info' in session:
        return redirect(url_for('dashboard.home'))
    redirect_uri = url_for('auth.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route('/authorize')
def authorize():
    def handle_auth_error():
        # noinspection PyTypeChecker
        flash({"title": "授權失敗", "content": "未能成功授權，請稍後再試，若此錯誤持續請與我們聯繫。"}, "popup_error")
        return redirect(url_for('index.home'))

    try:
        token = google.authorize_access_token()
        if not token:
            return handle_auth_error()

        resp = google.get('userinfo')
        if resp.status_code != 200:
            return handle_auth_error()

        user_info = resp.json()

        user = User.objects(google_id=user_info['id']).first() or User.create_user(
            google_id=user_info['id'],
            email=user_info['email'],
            name=user_info['name'],
            avatar_url=user_info['picture']
        )
        if user is None:
            return handle_auth_error()

        session['user_info'] = {
            'google_id': user.google_id,
            'name': user.name,
            'email': user.email,
            'avatar_url': user.avatar_url
        }

        session.permanent = True
        session.modified = True

        return redirect(url_for('dashboard.home'))
    except Exception as e:
        print(e)
        return handle_auth_error()


@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('user_info', None)
    # noinspection PyTypeChecker
    flash({"title": "登出成功", "content": "您已成功登出。"}, "popup_success")
    return redirect(url_for('index.home'))
