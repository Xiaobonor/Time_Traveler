# app/routes/plan.py
import asyncio
import pickle

from flask import Blueprint, render_template, request, jsonify, session

from app.utils.agents.assistant.travel_needs import TravelDemandAnalysisExpert
from app.utils.agents.assistant.travel_plan import TravelPlanExpert
from app.utils.agents.travel_needs_reviewer import travel_needs_check
from app.utils.auth_utils import login_required
from app.utils.turnstile import turnstile_required
from app.utils.callback import status_callback

plan_bp = Blueprint('plan', __name__)


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
        user_id = session['user_info']['google_id']
        agent = TravelDemandAnalysisExpert(callback=status_callback)
        status_callback("正在分析旅行需求...", "status", user_id)
        session['trip_plan'] = {}
        session['trip_plan']['agent'] = pickle.dumps(agent)
        session['trip_plan']['answers'] = {}
        session['trip_plan']['user_input'] = user_input
        thread_id = asyncio.run(agent.get_thread_id())
        response = asyncio.run(agent.submit_analysis_request(user_input))
        status_callback("旅行需求分析完成", "status", user_id)
        return jsonify({'success': True, 'questions': response, 'thread_id': thread_id})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@plan_bp.route('/submit_answers', methods=['POST'])
@login_required
@turnstile_required
def submit_answers():
    if 'trip_plan' not in session:
        return jsonify({'success': False, 'error': 'No trip_plan found in session'})

    data = request.json
    answers = data['answers']
    session_answers = session['trip_plan']['answers']
    session_answers.update(answers)
    session_answers = "使用者的旅行輸入(希望的旅程：" + session['trip_plan']['user_input'] + str(session_answers)
    user_id = session['user_info']['google_id']

    try:
        agent = pickle.loads(session['trip_plan']['agent'])
        status_callback("正在審核旅行需求...", "status", user_id)
        response, usage = asyncio.run(travel_needs_check(session_answers))
        if not response['success']:
            status_callback("旅行需求需進一步調整...", "status", user_id)
            thread_id = asyncio.run(agent.get_thread_id())
            response = asyncio.run(agent.submit_analysis_request(response['comment']))
            status_callback("旅行需求調整完成", "status", user_id)
            return jsonify({'success': True, 'new_question': True, 'questions': response, 'thread_id': thread_id})
        else:
            status_callback("旅行需求審核完成", "status", user_id)
            del agent
            session.pop('trip_plan')
            agent = TravelPlanExpert(callback=status_callback)
            status_callback("正在規劃旅行計畫...", "status", user_id)
            response = asyncio.run(agent.start_travel_plan(session_answers))
            del agent
            status_callback("旅行計畫完成", "status", user_id)
            print("{'success': True, 'new_question': False, 'response': " + response + "}")
            return jsonify({'success': True, 'new_question': False, 'response': response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})