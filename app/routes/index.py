# app/routes/index.py
from flask import Blueprint, render_template, session, url_for

index_bp = Blueprint('index', __name__)


@index_bp.route('/')
def home():
    return render_template('index.html')