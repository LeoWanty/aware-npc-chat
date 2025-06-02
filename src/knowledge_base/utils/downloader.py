from pathlib import Path

import requests
import re

from bs4 import BeautifulSoup

# Define User-Agent globally for consistency
USER_AGENT = "FandomDumpDownloader/1.0 (HuggingFace Hackathon)"


def fetch_page_content(url: str) -> str:
    """
    Fetches the content of a web page.

    Args:
        url: The URL of the page to fetch.

    Returns:
        The content of the page as a string.

    Raises:
        requests.exceptions.HTTPError: If the request returns a 4xx or 5xx status code.
    """
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        raise


def get_xml_dump_url(html_content: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    form = soup.find('form', {'action': '/wiki/Special:Statistics'})
    if form:
        divs_with_id = form.find_all('div', id=True)
        for div in divs_with_id:
            if re.compile(r'^Current pages').search(div.get_text(strip=True)):
                return div.find('a')['href']
        else:
            raise EOFError("No div with text starting with 'Current pages' AND with href found within the form.")
    else:
        raise EOFError("No form with the specified action found.")


def download_file(url: str, output_path: Path, chunk_size: int = 8192):
    """
    Downloads a file from a URL and saves it to a local path.

    Args:
        url: The URL of the file to download.
        output_path: The local path where the file should be saved.
        chunk_size: The size of chunks to download in bytes.

    Raises:
        requests.exceptions.HTTPError: If the request returns a 4xx or 5xx status code.
    """
    headers = {"User-Agent": USER_AGENT}
    try:
        # Ensure the output directory exists
        output_dir = output_path.parent
        if output_dir:  # Check if output_dir is not an empty string (i.e. file is in current dir)
            output_dir.mkdir(exist_ok=True)

        with requests.get(url, headers=headers, stream=True,
                          timeout=600) as response:  # Increased timeout for large files
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
        print(f"File downloaded successfully: {output_path}")
    except requests.exceptions.RequestException as e:
        # Clean up partially downloaded file if error occurs
        if output_path.exists():
            output_path.unlink()
        raise requests.exceptions.RequestException(f"Error downloading file from {url} to {output_path}: {e}")
    except IOError as e:
        if output_path.exists():
            output_path.unlink()
        raise IOError(f"Error writing file {output_path}: {e}")
