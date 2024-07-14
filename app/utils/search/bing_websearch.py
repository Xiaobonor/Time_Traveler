# app/utils/search/bing_websearch.py
import os
import requests
import asyncio
import json_repair
from app.utils.search.webpage_content import get_webpage_content

# Load environment variables at the beginning
subscription_key = os.getenv('AZURE_BING_SEARCH_API_KEY')
endpoint = os.getenv('AZURE_BING_SEARCH_ENDPOINT')


async def web_search_bing(query: str, count=10, offset=0, web_page=True, image=False, news=False, video=False,
                          fetch_content=True, content_length_limit=3000):
    """
    Use Bing Web Search to search the web for results.
    :param query: What you want to search for.
    :param count: The number of results you want.
    :param offset: The number of results to skip.
    :param web_page: Whether to include web page results.
    :param image: Whether to include image results.
    :param news: Whether to include news results.
    :param video: Whether to include video results.
    :param fetch_content: Whether to fetch and display the content of the web page results.
    :param content_length_limit: Maximum number of characters to fetch for each webpage content.
    :return: A list of results, json format.
    """
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}

    response_filter = []
    if image:
        response_filter.append("images")
    elif news:
        response_filter.append("news")
    elif video:
        response_filter.append("videos")
    elif web_page:
        response_filter.append("webPages")

    params = {
        'q': query,
        'count': count,
        'offset': offset,
        'responseFilter': ','.join(response_filter)
    }

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        search_results = response.json()

        if 'webPages' in search_results and fetch_content:
            tasks = [get_webpage_content(page['url'], content_length_limit) for page in search_results['webPages']['value']]
            contents = await asyncio.gather(*tasks)

            for i, page in enumerate(search_results['webPages']['value']):
                title, content = contents[i]
                search_results['webPages']['value'][i]['content'] = {
                    'page_title': title,
                    'page_content': content
                }

        return json_repair.repair_json(str(search_results))
    except Exception as e:
        print(f"Bing Search: An error occurred: {e}")
        return None
