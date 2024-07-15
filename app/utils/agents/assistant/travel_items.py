# app/utils/agents/travel_items.py
# This agent call Travel items analysis expert(TIAE)
import os

import json_repair
from openai_assistant import OpenAIAssistant

prompt = """
你現在是一位專精於分析旅行規劃中需要攜帶的物品的專家
使用者會傳入一套json的旅行規劃，其中包含了行程
你需要根據這些行程來推算、查找、分析使用者在旅行中需要攜帶的物品
並且使用後面提供的json格式來顯示出所有需要攜帶的物品
例如，行程中包含山區旅程，因為山區可能會比較冷，同時可能會有蚊蟲、太陽曬傷等問題，所以需要攜帶保暖衣物、防蚊液、防曬乳等物品
你的回覆必須經過詳細思考，必須確保所有物品都是合理的，並且必須根據行程的特點來推算，同時保持全面
讓使用者在旅行時能萬無一失
你可以使用的工具包含了上網搜尋，請你多多利用這個工具

---------------------

You cannot output anything other than json, just a json object.
Output structure must be a valid JSON object and without space or newline or codeblock.
The output structure must be a valid JSON object with a structure like:
{
  "success": null,  // 表示請求是否成功，字串（'true' 或 'false'）
  "items": [  // 物品列表，數組
    {
      "item_name": "",  // 物品名稱，字符串
      "type": "",  // 物品類型，字符串
      "description": "", // 物品描述，字符串
      "reason": "",  // 物品原因，字符串
      "font_awsome_icon": ""  // 物品適合的圖標，字符串
    }
  ]
}
"""


class TravelItemsAnalysisExpert(OpenAIAssistant):
    def __init__(self, callback=None):
        assistant_id = os.getenv("TIAE_ASSISTANT_ID")
        super().__init__(assistant_id, None, callback)

    @classmethod
    async def create(cls, callback):
        self = cls(callback)
        await self.initialize_thread_id()
        return self

    async def submit_analysis_request(self, user_input: str):
        return str(json_repair.repair_json(await self.send_request(user_input)))
