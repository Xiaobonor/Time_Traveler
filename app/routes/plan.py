# app/routes/plan.py
import asyncio
import pickle
import uuid

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
    user_id = session['user_info']['google_id']
    request_id = str(uuid.uuid4())

    session['trip_plan'] = {
        'request_id': request_id,
        'user_input': user_input,
        'agent': pickle.dumps(TravelDemandAnalysisExpert(callback=status_callback)),
        'answers': {}
    }

    asyncio.run(submit_analysis_request(user_id, user_input, request_id))

    return jsonify({'success': True, 'request_id': request_id})


@plan_bp.route('/check_status', methods=['GET'])
@login_required
def check_status():
    request_id = request.args.get('id')
    trip_plan = session.get('trip_plan', {})

    if trip_plan.get('request_id') != request_id:
        return jsonify({'completed': False, 'error': 'Invalid request ID'})

    if trip_plan.get('completed'):
        return jsonify({'completed': True, 'response': trip_plan['response']})

    return jsonify({'completed': False})


async def submit_analysis_request(user_id, user_input, request_id):
    try:
        agent = pickle.loads(session['trip_plan']['agent'])
        status_callback("正在分析旅行需求...", "status", user_id)
        thread_id = await agent.get_thread_id()
        response = await agent.submit_analysis_request(user_input)
        status_callback("旅行需求分析完成", "status", user_id)
        session['trip_plan']['thread_id'] = thread_id
        session['trip_plan']['response'] = response
        session['trip_plan']['completed'] = True
    except Exception as e:
        print(f"Error: {e}")
        session['trip_plan']['completed'] = True
        session['trip_plan']['error'] = str(e)


@plan_bp.route('/submit_answers', methods=['POST'])
@login_required
@turnstile_required
def submit_answers():
    if 'trip_plan' not in session:
        return jsonify({'success': False, 'error': 'No trip_plan found in session'})

    session['trip_plan']['completed'] = False
    data = request.json
    answers = data['answers']
    session_answers = session['trip_plan']['answers']
    session_answers.update(answers)
    session['trip_plan']['answers'] = session_answers
    user_id = session['user_info']['google_id']

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(submit_final_plan(user_id))
    loop.close()

    return jsonify({'success': True, 'request_id': session['trip_plan']['request_id']})


async def submit_final_plan(user_id):
    try:
        agent = pickle.loads(session['trip_plan']['agent'])
        status_callback("正在審核旅行需求...", "status", user_id)
        session_answers = session['trip_plan']['answers']
        response, usage = await travel_needs_check(str(session_answers))

        if not response['success']:
            status_callback("旅行需求需進一步調整...", "status", user_id)
            response = await agent.submit_analysis_request(response['comment'])
            status_callback("旅行需求調整完成", "status", user_id)
            session['trip_plan']['response'] = response
            session['trip_plan']['new_question'] = True
        else:
            status_callback("旅行需求審核完成", "status", user_id)
            del agent
            session.pop('trip_plan')
            agent = TravelPlanExpert(callback=status_callback)
            status_callback("正在規劃旅行計畫...", "status", user_id)
            response = await agent.start_travel_plan(session_answers)
            del agent
            status_callback("旅行計畫完成", "status", user_id)
            session['trip_plan']['response'] = response
            session['trip_plan']['new_question'] = False
        session['trip_plan']['completed'] = True
    except Exception as e:
        print(f"Error: {e}")
        session['trip_plan']['completed'] = True
        session['trip_plan']['error'] = str(e)