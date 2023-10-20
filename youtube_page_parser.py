from contextlib import closing
from requests import get
from requests.exceptions import RequestException
from requests.models import Response

from typing import Optional

from bs4 import BeautifulSoup as bs

def parse_with_soup(resp: str) -> Optional[bs]:
    """parse_with_soup
    Uses BeautifulSoup to parse the html, returns the parsed version
    :param resp: response content from get_site_content
    """
    if resp is not None:
        parsed = bs(resp, 'html.parser')
        return parsed
    else:
        logError("Response is not valid")
        return None

def is_good_html_response(resp: Response) -> bool:
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 and content_type is not None
            and content_type.find('html') > -1)


def get_page(url: str) -> Optional[str]:
    try:
        with closing(get(url.strip(), stream=True)) as res:
            if is_good_html_response(res):
                return res.content
            return None
    except RequestException as e:
        print(f"RequestException: {e}")
        return None



def get_channel_id(channel_name: str) -> Optional[str]:
    url = f"https://www.youtube.com/@{channel_name}"
    page_content = get_page(url)

    if not page_content:
        return None

    
    parsed = parse_with_soup(page_content)

    if not parsed:
        return None

    body = parsed.body

    all_meta = list(filter(lambda x: x.has_attr("property") and x["property"] and x["property"] == "og:url", body.find_all("meta")))

    if len(all_meta) != 0:
        return all_meta[0]["content"].split("/")[-1]

    return None



