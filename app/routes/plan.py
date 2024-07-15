# app/routes/plan.py
import asyncio
import pickle
import time
import uuid

from flask import Blueprint, render_template, request, jsonify, session

from app.utils.agents.assistant.travel_needs import TravelDemandAnalysisExpert
from app.utils.agents.assistant.travel_plan import TravelPlanExpert
from app.utils.agents.travel_needs_reviewer import travel_needs_check
from app.utils.auth_utils import login_required
from app.utils.turnstile import turnstile_required
from app.utils.callback import status_callback

plan_bp = Blueprint('plan', __name__)

# session['trip_plan']['new_question'] = False
# session['trip_plan'][
#     'response'] = """{\n  \"success\": true,\n  \"total_sections\": 7,\n  \"days\": 4,\n  \"sections\": [\n    {\n      \"title\": \"\u53f0\u5317\u570b\u7acb\u6545\u5bae\u535a\u7269\u9662\",\n      \"description\": \"\u53f0\u5317\u570b\u7acb\u6545\u5bae\u535a\u7269\u9662\u6536\u85cf\u4e86\u8d85\u904e70\u842c\u4ef6\u4e2d\u570b\u6b77\u53f2\u6587\u7269\u8207\u85dd\u8853\u54c1\uff0c\u662f\u4e16\u754c\u4e0a\u6700\u5927\u7684\u4e2d\u570b\u85dd\u8853\u535a\u7269\u9928\u4e4b\u4e00\u3002\",\n      \"time\": \"09:00~12:00\",\n      \"do_what\": \"\u53c3\u89c0\",\n      \"image\": \"https://i.redd.it/9gtcctdbqfj11.jpg\",\n      \"location\": \"\u53f0\u5317\u5e02\u58eb\u6797\u5340\u81f3\u5584\u8def\u4e8c\u6bb5221\u865f\",\n      \"landmarks\": {\n        \"coordinates\": [121.5485, 25.1024],\n        \"name\": \"\u53f0\u5317\u570b\u7acb\u6545\u5bae\u535a\u7269\u9662\",\n        \"description\": \"\u53f0\u5317\u570b\u7acb\u6545\u5bae\u535a\u7269\u9662\u64c1\u6709\u8c50\u5bcc\u7684\u4e2d\u570b\u53e4\u4ee3\u6587\u7269\u548c\u85dd\u8853\u54c1\uff0c\u662f\u63a2\u7d22\u4e2d\u570b\u6587\u5316\u8207\u6b77\u53f2\u7684\u5fc5\u8a2a\u4e4b\u5730\u3002\"\n      },\n      \"transportation\": \"\u642d\u4e58\u6377\u904b\u6de1\u6c34\u4fe1\u7fa9\u7dda\u81f3\u58eb\u6797\u7ad9\uff0c\u518d\u8f49\u4e58\u7d0530\u3001\u7d0513\u516c\u8eca\u81f3\u6545\u5bae\u535a\u7269\u9662\",\n      \"accommodation\": \"\",\n      \"restaurant\": \"\",\n      \"activity\": \"\",\n      \"youtube_url\": [\n        {\n          \"title\": \"\u53f0\u5317\u6545\u5bae\u535a\u7269\u9662-\u570b\u5bf6\u73cd\u85cf\",\n          \"url\": \"https://www.youtube.com/watch?v=RntSvFprl0w\"\n        }\n      ]\n    },\n    {\n      \"title\": \"\u53f0\u5357\u5b54\u5edf\",\n      \"description\": \"\u53f0\u5357\u5b54\u5edf\u5efa\u65bc1665\u5e74\uff0c\u662f\u53f0\u7063\u7b2c\u4e00\u5ea7\u5b54\u5edf\uff0c\u8c61\u5fb5\u8457\u53f0\u7063\u5112\u5bb6\u6587\u5316\u7684\u767c\u6e90\u5730\u3002\",\n      \"time\": \"13:00~14:30\",\n      \"do_what\": \"\u53c3\u89c0\",\n      \"image\": \"https://images.squarespace-cdn.com/content/v1/5438e2c6e4b0b18459a8ca06/1492709633018-8VIN78TFJKPWRJFMFMBW/image-asset.jpeg\",\n      \"location\": \"\u53f0\u5357\u5e02\u4e2d\u897f\u5340\u5357\u9580\u8def2\u865f\",\n      \"landmarks\": {\n        \"coordinates\": [120.2038, 22.9912],\n        \"name\": \"\u53f0\u5357\u5b54\u5edf\",\n        \"description\": \"\u53f0\u5357\u5b54\u5edf\u662f\u53f0\u7063\u6700\u53e4\u8001\u7684\u5b54\u5edf\uff0c\u662f\u5112\u5bb6\u6587\u5316\u7684\u91cd\u8981\u8c61\u5fb5\uff0c\u4fdd\u5b58\u8457\u8c50\u5bcc\u7684\u6b77\u53f2\u907a\u8de1\u548c\u6587\u7269\u3002\"\n      },\n      \"transportation\": \"\u5f9e\u53f0\u5357\u706b\u8eca\u7ad9\u642d\u4e58\u516c\u8eca\u81f3\u5b54\u5edf\u7ad9\u4e0b\u8eca\",\n      \"accommodation\": \"\",\n      \"restaurant\": \"\",\n      \"activity\": \"\",\n      \"youtube_url\": [\n        {\n          \"title\": \"\u53f0\u5357\u5b54\u5edf\u5c0e\u89bd\",\n          \"url\": \"https://www.youtube.com/watch?v=LRU99q94xA4\"\n        }\n      ]\n    },\n    {\n      \"title\": \"\u53f0\u5317\u570b\u7acb\u53f0\u7063\u535a\u7269\u9928\",\n      \"description\": \"\u53f0\u5317\u570b\u7acb\u53f0\u7063\u535a\u7269\u9928\u6210\u7acb\u65bc1908\u5e74\uff0c\u662f\u53f0\u7063\u6b77\u53f2\u6700\u60a0\u4e45\u7684\u535a\u7269\u9928\uff0c\u5c55\u793a\u6709\u95dc\u53f0\u7063\u6b77\u53f2\u3001\u6587\u5316\u8207\u81ea\u7136\u751f\u614b\u7684\u5404\u985e\u5c55\u54c1\u3002\",\n      \"time\": \"15:30~17:30\",\n      \"do_what\": \"\u53c3\u89c0\",\n      \"image\": \"https://upload.wikimedia.org/wikipedia/commons/8/88/2018_2287_Taiwan_NTM_2.jpg\",\n      \"location\": \"\u53f0\u5317\u5e02\u4e2d\u6b63\u5340\u8944\u967d\u8def42\u865f\",\n      \"landmarks\": {\n        \"coordinates\": [121.5140, 25.0452],\n        \"name\": \"\u53f0\u5317\u570b\u7acb\u53f0\u7063\u535a\u7269\u9928\",\n        \"description\": \"\u570b\u7acb\u53f0\u7063\u535a\u7269\u9928\u5c55\u793a\u4e86\u53f0\u7063\u8c50\u5bcc\u7684\u81ea\u7136\u8cc7\u6e90\u3001\u6587\u5316\u907a\u7522\u4ee5\u53ca\u6b77\u53f2\u6f14\u8b8a\uff0c\u70ba\u8a2a\u5ba2\u63d0\u4f9b\u6df1\u5165\u4e86\u89e3\u53f0\u7063\u7684\u6a5f\u6703\u3002\"\n      },\n      \"transportation\": \"\u642d\u4e58\u6377\u904b\u677f\u5357\u7dda\u81f3\u53f0\u5317\u8eca\u7ad9\uff0c\u6b65\u884c\u524d\u5f80\u535a\u7269\u9928\",\n      \"accommodation\": \"\",\n      \"restaurant\": \"\",\n      \"activity\": \"\",\n      \"youtube_url\": [\n        {\n          \"title\": \"\u570b\u7acb\u53f0\u7063\u535a\u7269\u9928\u4ecb\u7d39\",\n          \"url\": \"https://www.youtube.com/watch?v=3q0ZxmbnDaU\"\n        }\n      ]\n    },\n    {\n      \"title\": \"\u53f0\u5357\u8d64\u5d01\u6a13\",\n      \"description\": \"\u8d64\u5d01\u6a13\u5efa\u65bc1653\u5e74\uff0c\u539f\u540d\u666e\u7f85\u6c11\u906e\u57ce\uff0c\u662f\u53f0\u7063\u91cd\u8981\u7684\u6b77\u53f2\u53e4\u8e5f\u4e4b\u4e00\u3002\",\n      \"time\": \"09:00~11:00\",\n      \"do_what\": \"\u53c3\u89c0\",\n      \"image\": \"https://thumbs.dreamstime.com/b/night-view-chihkan-tower-tainan-taiwan-137982491.jpg\",\n      \"location\": \"\u53f0\u5357\u5e02\u4e2d\u897f\u5340\u6c11\u65cf\u8def\u4e8c\u6bb5212\u865f\",\n      \"landmarks\": {\n        \"coordinates\": [120.2026, 22.9972],\n        \"name\": \"\u8d64\u5d01\u6a13\",\n        \"description\": \"\u8d64\u5d01\u6a13\u662f\u53f0\u5357\u5e02\u7684\u91cd\u8981\u5730\u6a19\uff0c\u5305\u542b\u591a\u5ea7\u53e4\u5efa\u7bc9\u548c\u8c50\u5bcc\u7684\u6b77\u53f2\u6587\u7269\uff0c\u662f\u53f0\u7063\u6b77\u53f2\u7684\u91cd\u8981\u898b\u8b49\u3002\"\n      },\n      \"transportation\": \"\u5f9e\u53f0\u5357\u706b\u8eca\u7ad9\u642d\u4e58\u516c\u8eca\u81f3\u8d64\u5d01\u6a13\u7ad9\u4e0b\u8eca\",\n      \"accommodation\": \"\",\n      \"restaurant\": \"\",\n      \"activity\": \"\",\n      \"youtube_url\": [\n        {\n          \"title\": \"\u53f0\u5357\u8d64\u5d01\u6a13\u6b77\u53f2\u4ecb\u7d39\",\n          \"url\": \"https://www.youtube.com/watch?v=FhsXKtHyDG4\"\n        }\n      ]\n    },\n    {\n      \"title\": \"\u6797\u5b89\u6cf0\u53e4\u539d\",\n      \"description\": \"\u6797\u5b89\u6cf0\u53e4\u539d\u662f\u4fdd\u5b58\u826f\u597d\u7684\u53f0\u7063\u50b3\u7d71\u95a9\u5357\u5f0f\u5efa\u7bc9\uff0c\u5145\u6eff\u6fc3\u539a\u7684\u6b77\u53f2\u8207\u6587\u5316\u6c1b\u570d\u3002\",\n      \"time\": \"11:30~13:00\",\n      \"do_what\": \"\u53c3\u89c0\",\n      \"image\": \"https://upload.wikimedia.org/wikipedia/commons/1/18/2016_2287.jpg\",\n      \"location\": \"\u53f0\u5317\u5e02\u4e2d\u5c71\u5340\u6ff1\u6c5f\u88575\u865f\",\n      \"landmarks\": {\n        \"coordinates\": [121.5275, 25.0654],\n        \"name\": \"\u6797\u5b89\u6cf0\u53e4\u539d\",\n        \"description\": \"\u6797\u5b89\u6cf0\u53e4\u539d\u662f\u4e00\u5ea7\u64c1\u6709\u767e\u5e74\u6b77\u53f2\u7684\u95a9\u5357\u5efa\u7bc9\uff0c\u5176\u4fdd\u5b58\u5b8c\u5584\u7684\u5efa\u7bc9\u98a8\u683c\u548c\u5167\u90e8\u9673\u8a2d\u5c55\u73fe\u4e86\u53f0\u7063\u50b3\u7d71\u6587\u5316\u7684\u9b45\u529b\u3002\"\n      },\n      \"transportation\": \"\u642d\u4e58\u6377\u904b\u81f3\u5713\u5c71\u7ad9\uff0c\u6b65\u884c\u524d\u5f80\",\n      \"accommodation\": \"\",\n      \"restaurant\": \"\",\n      \"activity\": \"\",\n      \"youtube_url\": [\n        {\n          \"title\": \"\u6797\u5b89\u6cf0\u53e4\u539d\u6b77\u53f2\u4ecb\u7d39\",\n          \"url\": \"https://www.youtube.com/watch?v=u_dIrpQJ_r8\"\n        }\n      ]\n    },\n    {\n      \"title\": \"\u53f0\u5357\u6797\u767e\u8ca8\",\n      \"description\": \"\u6797\u767e\u8ca8\u5efa\u65bc1932\u5e74\uff0c\u662f\u53f0\u7063\u50c5\u5b58\u7684\u6230\u524d\u767e\u8ca8\u516c\u53f8\u5efa\u7bc9\u4e4b\u4e00\u3002\",\n      \"time\": \"14:00~15:30\",\n      \"do_what\": \"\u53c3\u89c0\u3001\u8cfc\u7269\",\n      \"image\": \"https://upload.wikimedia.org/wikipedia/commons/0/0d/Hayashi_Department_Store.jpg\",\n      \"location\": \"\u53f0\u5357\u5e02\u4e2d\u897f\u5340\u5fe0\u7fa9\u8def\u4e8c\u6bb563\u865f\",\n      \"landmarks\": {\n        \"coordinates\": [120.2036, 22.9937],\n        \"name\": \"\u6797\u767e\u8ca8\",\n        \"description\": \"\u6797\u767e\u8ca8\u878d\u5408\u4e86\u73fe\u4ee3\u8207\u50b3\u7d71\u7684\u5546\u696d\u6587\u5316\uff0c\u9664\u4e86\u8cfc\u7269\u5916\uff0c\u9084\u53ef\u4ee5\u611f\u53d7\u5176\u80cc\u5f8c\u8c50\u5bcc\u7684\u6b77\u53f2\u6545\u4e8b\u3002\"\n      },\n      \"transportation\": \"\u5f9e\u8d64\u5d01\u6a13\u6b65\u884c\u524d\u5f80\",\n      \"accommodation\": \"\",\n      \"restaurant\": \"\",\n      \"activity\": \"\",\n      \"youtube_url\": [\n        {\n          \"title\": \"\u53f0\u5357\u6797\u767e\u8ca8\u6545\u4e8b\",\n          \"url\": \"https://www.youtube.com/watch?v=z4-veHmrK2A\"\n        }\n      ]\n    }\n  ]\n}"""


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


@plan_bp.route('/check_status', methods=['POST'])
@login_required
def check_status():
    data = request.json
    request_id = data.get('id')
    trip_plan = session.get('trip_plan', {})

    if trip_plan.get('request_id') != request_id:
        return jsonify({'completed': False, 'error': 'Invalid request ID'})

    if trip_plan.get('completed'):
        return jsonify({'completed': True, 'response': trip_plan['response'], 'new_question': trip_plan.get('new_question', False)})

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
        session['trip_plan']['completed'] = True
    except Exception as e:
        print(f"Error: {e}")
        session['trip_plan']['completed'] = True
        session['trip_plan']['error'] = str(e)
