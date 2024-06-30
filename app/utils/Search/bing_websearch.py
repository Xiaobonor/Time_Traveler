#app/utils/Search/bing_websearch.py
import os
from web_search_client import WebSearchClient
from azure.core.credentials import AzureKeyCredential


def result_types_lookup():
    """WebSearchResultTypesLookup.

    This function looks up a single query (Xbox) and prints out the name and URL for the first web, image, news, and video results.
    """
    client = WebSearchClient(endpoint=ENDPOINT, credential=AzureKeyCredential(SUBSCRIPTION_KEY))

    try:
        web_data = client.web.search(query="xbox")
        print('Searched for Query# "Xbox"')

        # WebPages
        if web_data.web_pages and web_data.web_pages.value:
            print(f"Webpage Results#{len(web_data.web_pages.value)}")
            first_web_page = web_data.web_pages.value[0]
            print(f"First web page name: {first_web_page.name}")
            print(f"First web page URL: {first_web_page.url}")
        else:
            print("Didn't see any Web data.")

        # Images
        if web_data.images and web_data.images.value:
            print(f"Image Results#{len(web_data.images.value)}")
            first_image = web_data.images.value[0]
            print(f"First Image name: {first_image.name}")
            print(f"First Image URL: {first_image.url}")
        else:
            print("Didn't see any Images.")

        # News
        if web_data.news and web_data.news.value:
            print(f"News Results#{len(web_data.news.value)}")
            first_news = web_data.news.value[0]
            print(f"First News name: {first_news.name}")
            print(f"First News URL: {first_news.url}")
        else:
            print("Didn't see any News.")

        # Videos
        if web_data.videos and web_data.videos.value:
            print(f"Videos Results#{len(web_data.videos.value)}")
            first_video = web_data.videos.value[0]
            print(f"First Videos name: {first_video.name}")
            print(f"First Videos URL: {first_video.url}")
        else:
            print("Didn't see any Videos.")

    except Exception as err:
        print(f"Encountered exception: {err}")

if __name__ == "__main__":
    result_types_lookup()