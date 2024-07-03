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
            # response="""{"success":true,"total_sections":6,"sections":[{"title":"台北101","description":"台北101是台灣的象徵，也是台北市的地標之一。它擁有88樓到91樓的觀景台，提供了360度的全景視角。101樓的露天觀景台也是特別的體驗之一。","image":"https://www.taipei-101.com.tw/en/observatory/ticket/information","location":"台北市信義區市府路45號","landmarks":{"coordinates":[121.5654,25.0330],"name":"台北101觀景台","description":"台北101觀景台位於101大樓的88至91樓，提供驚人的城市全景。"},"transportation":"自駕車或台北捷運赤線到台北101/世貿站","accommodation":"台北市中心的民宿","restaurant":"西式餐廳","activity":"台北101觀景台參觀"},{"title":"士林夜市","description":"士林夜市是台灣最著名的夜市之一，提供各種美食和夜市遊戲，代表了繁華的台灣夜生活文化。","image":"https://www.nickkembel.com/best-taipei-night-markets","location":"台北市士林區大東路、大南路和周圍街巷","landmarks":{"coordinates":[121.5254,25.0874],"name":"士林夜市","description":"士林夜市以其豐富多樣的小吃和玩樂寶地而聞名，是體驗台北夜生活的絕佳去處。"},"transportation":"自駕車或台北捷運淡水信義線士林站","accommodation":"靠近士林區的民宿","restaurant":"士林夜市內的美食攤位","activity":"夜市遊玩和購物"},{"title":"台北孔廟","description":"台北孔廟是台灣少數保存完整的古蹟之一，以其傳統的中國建築風格和文化意象著稱。","image":"https://www.travel.taipei/en/must-visit/attractions-top25","location":"台北市大同區大龍街275號","landmarks":{"coordinates":[121.5145,25.0723],"name":"台北孔廟","description":"台北孔廟設計融合中國傳統建築與現代科技，並展示了豐富的文化文物。"},"transportation":"自駕車或台北捷運淡水信義線圓山站","accommodation":"靠近大同區的民宿","restaurant":"傳統台灣美食","activity":"文化探索和歷史古蹟參觀"},{"title":"Journey Town Inn","description":"Journey Town Inn 是台北市中心一家受歡迎的民宿，提供舒適和便利的住宿選擇。","image":"https://www.booking.com/bed-and-breakfast/city/tw/t-ai-pei.html","location":"台北市中山區","landmarks":{"coordinates":[121.5389,25.0536],"name":"Journey Town Inn","description":"這間民宿現代化的設計和共用休息室使其成為旅客們的理想選擇。"},"transportation":"自駕車或台北捷運中山站","accommodation":"Journey Town Inn","restaurant":"附近有多家西式餐廳","activity":"夜市逛街和城市探索"},{"title":"Gharry Car Rental","description":"Gharry Car Rental 提供台北的自駕租車服務，讓您自由探索這座城市。","image":"https://gharry.com.tw/en/index_2.php","location":"台北市中心","landmarks":{"coordinates":[121.5654,25.0330],"name":"Gharry Car Rental","description":"提供競爭力的價格和多樣的車型選擇，是自駕遊台北的理想選擇。"},"transportation":"自駕租車","accommodation":"不同地區的民宿","restaurant":"西式餐廳","activity":"城市探索和自駕"},{"title":"The Diner","description":"The Diner 是台北市中提供多樣化西式美食的餐廳，深受西方人士喜愛。","image":"https://www.taipeitravelgeek.com/best-western-restaurants-in-taipei","location":"台北市大安區","landmarks":{"coordinates":[121.5439,25.0326],"name":"The Diner","description":"這家餐廳以其豐富的西式早餐、早午餐和午餐聞名，擁有寬敞的用餐環境。"},"transportation":"自駕車或台北捷運東門站","accommodation":"附近的民宿","restaurant":"The Diner","activity":"用餐和購物"}]}"""
            del agent
            status_callback("旅行計畫完成", "status", user_id)
            return jsonify({'success': True, 'new_question': False, 'response': response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})