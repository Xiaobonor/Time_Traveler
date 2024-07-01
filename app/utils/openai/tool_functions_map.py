# app/utils/openai/tool_functions_map.py
from typing import Callable, Dict
from app.utils.search.bing_websearch import web_search_bing


FUNCTION_MAP: Dict[str, Callable] = {
    "web_search_bing": web_search_bing,
}


def get_function(name: str) -> Callable:
    return FUNCTION_MAP.get(name)
