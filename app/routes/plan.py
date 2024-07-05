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

    agent = asyncio.run(TravelDemandAnalysisExpert.create(callback=status_callback))

    session['trip_plan'] = {
        'request_id': request_id,
        'user_input': user_input,
        'agent': pickle.dumps(agent),
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
            agent = await TravelPlanExpert.create(callback=status_callback)
            status_callback("正在規劃旅行計畫...", "status", user_id)
            response = await agent.start_travel_plan(str(session_answers))
            del agent
            status_callback("旅行計畫完成", "status", user_id)
            session['trip_plan']['response'] = response
            session['trip_plan']['new_question'] = False
            # session['trip_plan']['response'] = """{\"success\":true,\"total_sections\":5,\"sections\":[{\"title\":\"\u81fa\u5317101\",\"description\":\"\u81fa\u5317101\u4f4d\u65bc\u81fa\u7063\u81fa\u5317\u5e02\u4fe1\u7fa9\u5340\uff0c\u66fe\u70ba\u4e16\u754c\u6700\u9ad8\u6a13\u3002\u9664\u4e86\u662f\u8cfc\u7269\u548c\u8fa6\u516c\u7684\u4e2d\u5fc3\uff0c\u5b83\u7684\u89c0\u666f\u53f0\u63d0\u4f9b\u58ef\u89c0\u7684\u57ce\u5e02\u666f\u8272\u3002\",\"time\":\"\u7b2c\u4e00\u5929 10:00-12:00\",\"image\":\"https://www.taipeitravelgeek.com/taipei-101\",\"location\":\"\u81fa\u5317\u5e02\u4fe1\u7fa9\u5340\u4fe1\u7fa9\u8def\u4e94\u6bb57\u865f89\u6a13\",\"landmarks\":{\"coordinates\":[121.5656,25.0339],\"name\":\"\u81fa\u5317101\",\"description\":\"\u81fa\u7063\u7684\u6a19\u8a8c\u6027\u5efa\u7bc9\uff0c\u66fe\u70ba\u4e16\u754c\u6700\u9ad8\u6a13\"},\"transportation\":\"\u5305\u8eca\",\"accommodation\":\"\u65b0\u5149\u5546\u65c5\",\"restaurant\":\"\u9f0e\u6cf0\u8c50\",\"activity\":\"\u89c0\u666f\u53f0\",\"youtube_url\":[{\"title\":\"Taipei 101 Tower Tour\",\"url\":\"https://www.youtube.com/watch?v=cgWv7pz5nok\"}]},{\"title\":\"\u967d\u660e\u5c71\u570b\u5bb6\u516c\u5712\",\"description\":\"\u967d\u660e\u5c71\u570b\u5bb6\u516c\u5712\u63d0\u4f9b\u8c50\u5bcc\u7684\u81ea\u7136\u666f\u89c0\uff0c\u5305\u62ec\u706b\u5c71\u3001\u7011\u5e03\u548c\u82b1\u6d77\uff0c\u662f\u4f11\u9592\u548c\u81ea\u7136\u611b\u597d\u8005\u7684\u6a02\u5712\u3002\",\"time\":\"\u7b2c\u4e8c\u5929 09:00-17:00\",\"image\":\"https://www.thebrokebackpacker.com/best-places-to-visit-in-taipei/\",\"location\":\"\u81fa\u5317\u5e02\u5317\u6295\u5340\u7af9\u5b50\u6e56\u8def\",\"landmarks\":{\"coordinates\":[121.519,25.179],\"name\":\"\u967d\u660e\u5c71\u570b\u5bb6\u516c\u5712\",\"description\":\"\u81fa\u7063\u77e5\u540d\u7684\u570b\u5bb6\u516c\u5712\uff0c\u6709\u591a\u6a23\u7684\u81ea\u7136\u666f\u89c0\"},\"transportation\":\"\u5305\u8eca\",\"accommodation\":\"\u65b0\u5149\u5546\u65c5\",\"restaurant\":\"\u4e2d\u5348\u53ef\u65bc\u5712\u5340\u5167\u9910\u5ef3\u4eab\u7528\",\"activity\":\"\u81ea\u7136\u63a2\u7d22\",\"youtube_url\":[{\"title\":\"Visit Yangmingshan National Park\",\"url\":\"https://www.youtube.com/watch?v=dP_nhQTDYXU\"}]},{\"title\":\"\u4e5d\u4efd\u8001\u8857\",\"description\":\"\u4e5d\u4efd\u8001\u8857\u5145\u6eff\u6fc3\u539a\u7684\u6b77\u53f2\u6c1b\u570d\uff0c\u662f\u81fa\u7063\u8457\u540d\u7684\u89c0\u5149\u9ede\uff0c\u4ee5\u5176\u7368\u7279\u7684\u65e5\u5f0f\u5efa\u7bc9\u548c\u7f8e\u98df\u8457\u7a31\u3002\",\"time\":\"\u7b2c\u4e09\u5929 09:00-17:00\",\"image\":\"https://www.myglobalviewpoint.com/most-beautiful-places-in-taipei/\",\"location\":\"\u65b0\u5317\u5e02\u745e\u82b3\u5340\u5751\u5c3e\u8def\",\"landmarks\":{\"coordinates\":[121.8447,25.1095],\"name\":\"\u4e5d\u4efd\u8001\u8857\",\"description\":\"\u6b77\u53f2\u60a0\u4e45\u7684\u91d1\u7926\u5c0f\u93ae\uff0c\u4ee5\u5176\u7f8e\u98df\u548c\u53e4\u98a8\u5efa\u7bc9\u5438\u5f15\u904a\u5ba2\"},\"transportation\":\"\u5305\u8eca\",\"accommodation\":\"\u65b0\u5149\u5546\u65c5\",\"restaurant\":\"\u8001\u8857\u5404\u5730\u6524\u5c0f\u5403\",\"activity\":\"\u6b77\u53f2\u63a2\u7d22\",\"youtube_url\":[{\"title\":\"Exploring Jiufen Old Street\",\"url\":\"https://www.youtube.com/watch?v=LwPY7ybUglI\"}]},{\"title\":\"\u6de1\u6c34\",\"description\":\"\u6de1\u6c34\u64c1\u6709\u8c50\u5bcc\u7684\u6587\u5316\u548c\u81ea\u7136\u666f\u89c0\uff0c\u662f\u81fa\u5317\u5468\u908a\u7684\u71b1\u9580\u65c5\u904a\u76ee\u7684\u5730\u3002\",\"time\":\"\u7b2c\u56db\u5929 10:00-17:00\",\"image\":\"https://www.busytourist.com/things-to-do-in-taipei/\",\"location\":\"\u65b0\u5317\u5e02\u6de1\u6c34\u5340\",\"landmarks\":{\"coordinates\":[121.4331,25.1796],\"name\":\"\u6de1\u6c34\",\"description\":\"\u5145\u6eff\u6b77\u53f2\u8207\u6587\u5316\u7684\u89c0\u5149\u52dd\u5730\"},\"transportation\":\"\u5305\u8eca\",\"accommodation\":\"\u65b0\u5149\u5546\u65c5\",\"restaurant\":\"\u7576\u5730\u5c0f\u5403\",\"activity\":\"\u6587\u5316\u63a2\u7d22\",\"youtube_url\":[{\"title\":\"A Visit to Tamsui\",\"url\":\"https://www.youtube.com/watch?v=m4fRQD1tXEA\"}]},{\"title\":\"\u77f3\u9580\u6c34\u5eab\",\"description\":\"\u77f3\u9580\u6c34\u5eab\u662f\u81fa\u7063\u8457\u540d\u7684\u4f11\u9592\u666f\u9ede\uff0c\u63d0\u4f9b\u6c34\u4e0a\u6d3b\u52d5\u548c\u81ea\u7136\u666f\u89c0\u3002\",\"time\":\"\u7b2c\u4e94\u5929 09:00-17:00\",\"image\":\"https://www.busytourist.com/things-to-do-in-taipei/\",\"location\":\"\u65b0\u5317\u5e02\u4e09\u5cfd\u5340\",\"landmarks\":{\"coordinates\":[121.367,24.937],\"name\":\"\u77f3\u9580\u6c34\u5eab\",\"description\":\"\u77e5\u540d\u7684\u907f\u6691\u52dd\u5730\uff0c\u9069\u5408\u9032\u884c\u6c34\u4e0a\u6d3b\u52d5\"},\"transportation\":\"\u5305\u8eca\",\"accommodation\":\"\u65b0\u5149\u5546\u65c5\",\"restaurant\":\"\u81ea\u5099\u5348\u9910\u91ce\u9910\",\"activity\":\"\u6c34\u4e0a\u6d3b\u52d5\",\"youtube_url\":[{\"title\":\"Day trip to Shihmen Reservoir\",\"url\":\"https://www.youtube.com/watch?v=GQJqLOKMbzE\"}]}]}"""
            # session['trip_plan']['new_question'] = False
        session['trip_plan']['completed'] = True
    except Exception as e:
        print(f"Error: {e}")
        session['trip_plan']['completed'] = True
        session['trip_plan']['error'] = str(e)
