# app/routes/plan.py
import asyncio
import pickle
import uuid
from threading import Thread

from flask import Blueprint, render_template, request, jsonify, session, copy_current_request_context

from app.utils.agents.assistant.travel_needs import TravelDemandAnalysisExpert
from app.utils.agents.assistant.travel_plan import TravelPlanExpert
from app.utils.agents.assistant.travel_items import TravelItemsAnalysisExpert
from app.utils.travel_needs_reviewer import travel_needs_check
from app.utils.auth_utils import login_required
from app.utils.turnstile import turnstile_required
from app.utils.callback import status_callback
from app.utils.mail_sender import send_email


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


@plan_bp.route('/check_status', methods=['POST'])
@login_required
def check_status():
    data = request.json
    request_id = data.get('id')
    trip_plan = session.get('trip_plan', {})
    print(trip_plan)

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


def submit_final_plan(user_id):
    with copy_current_request_context():
        try:
            agent = pickle.loads(session['trip_plan']['agent'])
            status_callback("正在審核旅行需求...", "status", user_id)
            session_answers = session['trip_plan']['answers']
            response, usage = asyncio.run(travel_needs_check(str(session_answers)))

            if not response['success']:
                status_callback("旅行需求需進一步調整...", "status", user_id)
                response = asyncio.run(agent.submit_analysis_request(response['comment']))
                status_callback("旅行需求調整完成", "status", user_id)
                session['trip_plan']['response'] = response
                session['trip_plan']['new_question'] = True
            else:
                status_callback("旅行需求審核完成", "status", user_id)
                del agent
                agent = asyncio.run(TravelPlanExpert.create(callback=status_callback))
                status_callback("正在規劃旅行計畫...", "status", user_id)
                response = asyncio.run(agent.start_travel_plan(str(session_answers)))
                del agent
                status_callback("旅行計畫完成", "status", user_id)
                session['trip_plan']['response'] = response
                session['trip_plan']['new_question'] = False
                agent = asyncio.run(TravelItemsAnalysisExpert.create(callback=status_callback))
                status_callback("正在分析旅行物品...", "status", user_id)
                response = asyncio.run(agent.submit_analysis_request(str(response)))
                print(response)
                print("------------------------------")
                items = response['items']
                print(items)
                send_email("情前物品提醒！", 'xiao.bo.nor@gmail.com', "email/travel_items.html", items=items)
                status_callback("旅行物品分析完成", "status", user_id)
                del agent
            session['trip_plan']['completed'] = True
            print("Trip plan completed")
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

    thread = Thread(target=submit_final_plan, args=(user_id,))
    thread.start()

    return jsonify({'success': True, 'request_id': session['trip_plan']['request_id']})


@plan_bp.route('/test')
def test():
    items = [
        {"item_name": "保暖衣物", "type": "衣物", "description": "防寒的外套或毛衣", "reason": "山區旅程可能會較冷", "font_awsome_icon": "fa-solid fa-jacket"},
        {"item_name": "防蚊液", "type": "衛生用品", "description": "防蚊蟲叮咬的噴霧或乳液", "reason": "山區可能有蚊蟲", "font_awsome_icon": "fa-solid fa-spray-can"},
        {"item_name": "防曬乳", "type": "衛生用品", "description": "防止紫外線傷害皮膚的乳液", "reason": "保護皮膚免受陽光直射", "font_awsome_icon": "fa-solid fa-sun"},
        {"item_name": "舒適步行鞋", "type": "衣物", "description": "穿著舒適的步行鞋", "reason": "行程中包含長時間步行", "font_awsome_icon": "fa-solid fa-shoe-prints"},
        {"item_name": "水瓶", "type": "設備", "description": "可重複使用的水瓶", "reason": "保持旅行中隨時補充水分", "font_awsome_icon": "fa-solid fa-water-bottle"},
        {"item_name": "口罩", "type": "衛生用品", "description": "一次性或可重複使用的口罩", "reason": "公共場所保護", "font_awsome_icon": "fa-solid fa-head-side-mask"},
        {"item_name": "手消毒液", "type": "衛生用品", "description": "便攜手消毒液", "reason": "保持手部衛生", "font_awsome_icon": "fa-solid fa-pump-soap"},
        {"item_name": "相機", "type": "設備", "description": "用於拍攝照片的相機", "reason": "旅行紀念和景點拍攝", "font_awsome_icon": "fa-solid fa-camera"},
        {"item_name": "充電器和充電寶", "type": "電子產品", "description": "手機及相機等設備的充電器和移動電源", "reason": "保持電子設備電量充足", "font_awsome_icon": "fa-solid fa-charging-station"},
        {"item_name": "舒適透氣的衣物", "type": "衣物", "description": "輕便且透氣的上衣和長褲", "reason": "參觀寺廟和博物館需要衣
