# app/utils/agents/travel_needs_check.py
import json_repair
from app.utils.openai.openai_chat import generate_text

prompt = """
你是一位專業的旅行行程分析師，你必須根據使用者傳入的旅行規劃與問題來分析這個旅行規劃是否為一個理想中的旅行行程？
理想中的旅行行程應該包含旅行中的各個規劃，包括旅行開始的
"""


async def travel_plan_reviewer(json_data):
    if "cf-turnstile-response" in json_data:
        del json_data["cf-turnstile-response"]

    response, usage = await generate_text(system_prompt=prompt, user_prompt=json_data)

    response = json_repair.repair_json(response)
    response_dict = json_repair.loads(response)

    if not response_dict['success']:
        response_dict[
            'comment'] = ("你的所列出的問題太少了，這是審評意見，請再增加更多問題，同時也請確保你的輸出內容應該只有json格式，不要有空格或換行。\
            同時請你僅列出新追問的問題和選項即可，不必列出剛剛已經有的選項。 Output structure must be a valid JSON object and " +
            "without space or newline.。") + response_dict['comment']

    return response_dict, usage
