# app/routes/plan.py
import asyncio
import pickle

from flask import Blueprint, render_template, request, jsonify, session

from app.utils.agents.assistant.travel_needs import TravelDemandAnalysisExpert
from app.utils.agents.travel_needs_check import travel_needs_check
from app.utils.auth_utils import login_required
from app.utils.turnstile import turnstile_required

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
        print(f"User input: {user_input}")
        agent = TravelDemandAnalysisExpert()
        session['agent'] = pickle.dumps(agent)
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
    if 'agent' not in session:
        return jsonify({'success': False, 'error': 'No agent found in session'})

    print("Got answers")
    data = request.json
    answers = data['answers']
    try:
        print("Submitting answers to review....")
        response, usage = asyncio.run(travel_needs_check(str(answers)))
        print(f"Response: {response['success']}, comment: {response['comment']}")
        if not response['success']:
            print("Reviewer think it was not a good request, get agent to ask again...")
            agent = pickle.loads(session.get('agent'))
            thread_id = asyncio.run(agent.get_thread_id())
            print(f"Thread ID: {thread_id}")
            print("Start question again...")
            response = asyncio.run(agent.submit_analysis_request(response['comment']))
            print(f"Response: {response}")
            return jsonify({'success': True, 'new_question': True, 'questions': response, 'thread_id': thread_id})
        else:
            print("Reviewer think it was a good request, returning success...")
            # TODO: generate trip plan
            return jsonify({'success': True, 'new_question': False, 'response': response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})
