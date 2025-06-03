import pytest

from knowledge_base.utils.url import get_fandom_statistics_page_url

@pytest.mark.parametrize("url, expected_output", zip([
    "https://asimov.fandom.com/wiki/Asimov_Wiki",
    "https://asimov.fandom.com/",
    "https://starwars.fandom.com/wiki/Main_Page",
], [
    "https://asimov.fandom.com/wiki/Special:Statistics",
    "https://asimov.fandom.com/wiki/Special:Statistics",
    "https://starwars.fandom.com/wiki/Special:Statistics",
]))
def test_get_fandom_statistics_page_url(url, expected_output):
    """Test the get_fandom_statistics_page_url function with various Fandom URLs."""
    result = get_fandom_statistics_page_url(url)
    assert result == expected_output, f"Test failed for {url}"


EXPECTED_OUTPUT = "https://fandom.com/wiki/Special:Statistics"


def test_get_fandom_statistics_page_url_with_different_schemes():
    """Test the function with URLs using different schemes (http/https)."""
    assert get_fandom_statistics_page_url("http://fandom.com") == "http://fandom.com/wiki/Special:Statistics"
    assert get_fandom_statistics_page_url("https://fandom.com") == EXPECTED_OUTPUT


def test_get_fandom_statistics_page_url_with_trailing_slash():
    """Test the function with URLs that have or don't have trailing slashes."""
    assert get_fandom_statistics_page_url("https://fandom.com/") == EXPECTED_OUTPUT
    assert get_fandom_statistics_page_url("https://fandom.com") == EXPECTED_OUTPUT
