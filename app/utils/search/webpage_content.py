# api/utils/search/webpage_content.py
import aiohttp
from bs4 import BeautifulSoup


async def get_webpage_content(url):
    """
    Fetch the content of a webpage asynchronously.
    :param url: The URL of the webpage.
    :return: The title and content of the webpage.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.string if soup.title else 'No Title'
                paragraphs = soup.find_all('p')
                content = '\n'.join([p.get_text() for p in paragraphs])
                return title, content
        except Exception as e:
            print(f"An error occurred while fetching the webpage content: {e}")
            return None, None
