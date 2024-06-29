# app/routes/plan.py
from flask import Blueprint, render_template, request, jsonify

from app.utils.auth_utils import login_required

plan_bp = Blueprint('plan', __name__)

mock_questions = [
    {
        'id': 1,
        'text': '您的旅程會有多少天？',
        'options': ['3天', '5天', '7天']
    },
    {
        'id': 2,
        'text': '您有多少人同行？',
        'options': ['1人', '2人', '3人']
    },
    {
        'id': 3,
        'text': '您對住宿有什麼要求？',
        'options': ['經濟型', '舒適型', '豪華型']
    }
]

mock_plan = {
    'schedule': 'Day 1: 抵達, Day 2: 觀光, Day 3: 返回',
    'attractions': '博物館, 公園, 海灘',
    'restaurants': '當地餐廳, 海鮮店, 咖啡廳',
    'accommodations': '酒店, 民宿, 度假村'
}

responses = {}

@plan_bp.route('/plan')
@login_required
def index():
    return render_template('plan.html')

@plan_bp.route('/submit_request', methods=['POST'])
@login_required
def submit_request():
    data = request.json
    initial_request = data['request']
    questions_to_ask = mock_questions  # Return all questions for now
    return jsonify({'questions': questions_to_ask})

@plan_bp.route('/submit_answers', methods=['POST'])
@login_required
def submit_answers():
    global responses
    data = request.json
    answers = data['answers']
    responses.update(answers)

    # For simplicity, assume no follow-up questions for now
    if len(responses) == len(mock_questions):
        return jsonify({'completed': True, 'plan': mock_plan})
    else:
        return jsonify({'completed': False, 'questions': [mock_questions[len(responses)]]})