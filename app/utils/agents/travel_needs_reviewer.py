# app/utils/agents/travel_needs_check.py
import json_repair
from app.utils.openai.openai_chat import generate_text

# If you want to make it always return false on first time, just add the following line:
# 你必須嚴格審查，其中必須有15個問題以上，否則就 false。
prompt = """你是一位專業的旅行需求分析師，你必須根據使用者給的json來分析它的旅行回答是否足以創建一個它理想中的旅行行程？
如果他的回答足夠，那請你在稍後的json中的"success"填入True；相反，如果他的回答不足以創建一個理想的旅行行程，那請你在稍後的json中的"success"填入False。
一個好的旅行行程需要好的旅行需求，所以你必須判斷是否僅能憑那些數據來進行一趟好的規劃。同時，若你認為數據(問題)不足，那也請你在json中加入你的審評意見，以及改善建議(需要增加哪些方向或類別的問題讓旅程建議更加完整)。

------------------------------

使用者提供的Json格式將為：
{
  "answers": {
    "範例問題1": "範例回答1",
    "範例問題2": "範例回答2",
  },
  "cf-turnstile-response": "範例問題2"
}

其中的answers將包含一個或多個問題的回答。

------------------------------

You cannot output anything other than json, just a json object.
Output structure must be a valid JSON object and without space or newline.
The output structure must be a valid JSON object with a structure like:
{
  "success": null,  // 表示請求是否成功，布爾值（true 或 false）
  "comment": "",  // 你的審評意見，字符串
}

"""


async def travel_needs_check(json_data):
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
