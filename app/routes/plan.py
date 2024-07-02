# app/routes/plan.py
import asyncio
from flask import Blueprint, render_template, request, jsonify

from app.utils.agents.travel_needs import TravelDemandAnalysisExpert
from app.utils.auth_utils import login_required
from app.utils.turnstile import turnstile_required

plan_bp = Blueprint('plan', __name__)

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
@turnstile_required
def submit_request():
    data = request.json
    user_input = data['request']
    try:
        print(f"User input: {user_input}")
        agent = TravelDemandAnalysisExpert()
        print("Created agent")
        thread_id = asyncio.run(agent.get_thread_id())
        print(f"Thread ID: {thread_id}")
        response = asyncio.run(agent.submit_analysis_request(user_input))
        print(f"Response: {response}")
        return jsonify({'success': True, 'questions': response, 'thread_id': thread_id})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@plan_bp.route('/submit_answers', methods=['POST'])
@login_required
@turnstile_required
def submit_answers():
    global responses
    data = request.json
    answers = data['answers']
    responses.update(answers)

    # For simplicity, assume no follow-up questions for now
    if len(answers) == len(mock_questions):
        return jsonify({'success': True, 'plan': mock_plan})
    else:
        return jsonify({'success': False, 'questions': [mock_questions[len(responses)]]})
