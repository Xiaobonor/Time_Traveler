# app/routes/flash_messages.py
from flask import Blueprint, jsonify, get_flashed_messages

flash_message_bp = Blueprint('flash_message', __name__)


@flash_message_bp.route('/flash_messages', methods=['POST'])
def get_messages():
    messages = get_flashed_messages(with_categories=True)
    response = {}
    for category, message in messages:
        if category == "popup_error":
            response["error"] = {"title": message["title"], "message": message["content"]}
        elif category == "popup_success":
            response["success"] = {"title": message["title"], "message": message["content"]}
    return jsonify(response)