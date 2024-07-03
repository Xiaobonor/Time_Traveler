# app/utils/openai/openai_assistant.py
# This file is a modified version of the chat_session.py from the repository at
# https://github.com/shamspias/openai-assistent-python/tree/main. This version has been
# modified by Xiaobonor.
import asyncio
from app.utils.openai.thread_manager import create_thread, list_messages, send_message, delete_thread, \
    create_run, get_runs_by_thread, submit_tool_outputs_and_poll
from app.utils.openai.tool_functions_map import get_function


class OpenAIAssistant:
    def __init__(self, assistant_id: str, thread_id: str = None, callback=None):
        self.assistant_id = assistant_id
        self.thread_id = thread_id if thread_id is not None else asyncio.run(create_thread(messages=[])).id
        self.callback = callback

    async def get_thread_id(self):
        return self.thread_id

    async def delete_current_thread(self):
        return await delete_thread(self.thread_id)

    async def send_request(self, message_content: str):
        await self._send_message(message_content)
        self.callback("正在等待助手回應...", "status")
        run = await self._initiate_run()
        await self._wait_for_assistant_response(run)
        return await self._retrieve_latest_assistant_response()

    async def _send_message(self, message_content: str):
        return await send_message(self.thread_id, message_content)

    async def _initiate_run(self):
        return await create_run(self.thread_id, self.assistant_id)

    async def _wait_for_assistant_response(self, run):
        while True:
            runs = await get_runs_by_thread(self.thread_id)
            running = runs.data[0]
            if running.status == "requires_action":
                self.callback("助手調用工具中...", "status")
                tool_outputs = await self._handle_tool_calls(running.required_action.submit_tool_outputs.tool_calls)
                self.callback("調用完成，等待助手回應...", "status")
                await submit_tool_outputs_and_poll(self.thread_id, running.id, tool_outputs)
                await self._poll_until_complete(running.id)
                break
            elif running.status in ["completed", "failed"]:
                self.callback("已完成任務", "status")
                break
            await asyncio.sleep(2)

    async def _poll_until_complete(self, run_id: str):
        while True:
            runs = await get_runs_by_thread(self.thread_id)
            running = runs.data[0]
            if running.status in ["requires_action"]:
                self.callback("助手調用工具中...", "status")
                tool_outputs = await self._handle_tool_calls(running.required_action.submit_tool_outputs.tool_calls)
                self.callback("調用完成，等待助手回應...", "status")
                await submit_tool_outputs_and_poll(self.thread_id, running.id, tool_outputs)
                await self._poll_until_complete(running.id)
                break
            elif running.status in ["completed", "failed"]:
                self.callback("已完成任務", "status")
                break
            await asyncio.sleep(2)

    async def _handle_tool_calls(self, tool_calls):
        output_list = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = tool_call.function.arguments

            if isinstance(function_args, str):
                function_args = eval(function_args.replace("true", "True").replace("false", "False"))

            function = get_function(function_name)
            if function:
                output = await function(**function_args)
                output_list.append({
                    "tool_call_id": tool_call.id,
                    "output": output
                })
        return output_list

    async def _retrieve_latest_assistant_response(self):
        messages = await list_messages(self.thread_id)
        for message in messages.data:
            if message.role == "assistant":
                return message.content[0].text.value
        return None
