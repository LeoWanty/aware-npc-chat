import urllib.parse


def _get_fandom_base_url(fandom_url: str) -> str:
    parsed_url = urllib.parse.urlparse(fandom_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def get_fandom_statistics_page_url(fandom_url: str) -> str:
    """
    Constructs the URL for the Special:Statistics page of a Fandom wiki.

    Args:
        fandom_url: The base URL of the Fandom wiki
            (e.g., "https://asimov.fandom.com/wiki/Asimov_Wiki" or "https://asimov.fandom.com/").

    Returns:
        The URL of the Special:Statistics page.
    """
    base_url = _get_fandom_base_url(fandom_url)
    statistics_path = "wiki/Special:Statistics"
    return urllib.parse.urljoin(base_url + "/", statistics_path)


def get_fandom_page_url(page_name: str, fandom_url: str) -> str:
    """
    Generates a Fandom wiki URL for a given character name.

    Args:
        page_name: The name of the page.
        fandom_url: An URL from the Fandom wiki
            (e.g., "https://asimov.fandom.com/wiki/Asimov_Wiki" or "https://asimov.fandom.com/").

    Returns:
        The constructed Fandom URL for the character.
    """
    base_url = _get_fandom_base_url(fandom_url)
    return urllib.parse.urljoin(base_url + "/", page_name)
