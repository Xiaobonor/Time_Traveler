# app/__init__.py
from urllib.parse import urlparse
from datetime import timedelta
import os

from flask import Flask
from flask_cors import CORS
from flask_session import Session
from flask_socketio import SocketIO

from dotenv import load_dotenv
from mongoengine import connect
from authlib.integrations.flask_client import OAuth
from async_openai import OpenAIClient
from redis import Redis

socketio = SocketIO()
cors = CORS()
oauth = OAuth()
openai = OpenAIClient()


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['DEBUG'] = os.getenv('DEBUG') == 'True'

    redis_url = urlparse(os.getenv('REDIS_URI'))
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = Redis(
        host=redis_url.hostname,
        port=redis_url.port,
        password=redis_url.password
    )
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') if os.getenv('SECRET_KEY') else os.urandom(24)
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=int(os.getenv('SESSION_TIMEOUT', 604800)))
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'sess:'

    # Here to load blueprint
    from app.routes.auth import auth_bp

    connect(host=os.getenv('MONGO_URI'))
    openai.api_key = os.getenv('OPENAI_API_KEY') if os.getenv('OPENAI_API_KEY') else None
    Session(app)
    socketio.init_app(app)
    oauth.init_app(app)
    cors.init_app(app)

    # Here to register blueprint
    app.register_blueprint(auth_bp)

    return app
