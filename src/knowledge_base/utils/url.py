import urllib.parse

def get_fandom_statistics_page_url(fandom_url: str) -> str:
    """
    Constructs the URL for the Special:Statistics page of a Fandom wiki.

    Args:
        fandom_url: The base URL of the Fandom wiki
                    (e.g., "https://asimov.fandom.com/wiki/Asimov_Wiki" or "https://asimov.fandom.com/").

    Returns:
        The URL of the Special:Statistics page.
    """
    parsed_url = urllib.parse.urlparse(fandom_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    statistics_path = "wiki/Special:Statistics"
    return urllib.parse.urljoin(base_url + "/", statistics_path)