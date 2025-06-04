import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image


def get_figure_html_from_fandom_page(url: str) -> str | None:
    # Fetch the HTML content from the URL
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    div_content = soup.find('div', id='content')
    figure = div_content.find('figure')  # Should be the first one
    if figure:
        return figure.find('a')['href']
    else:
        # "Image not found" image
        return "https://png.pngtree.com/png-clipart/20190925/original/pngtree-no-image-vector-illustration-isolated-png-image_4979075.jpg"


DEFAULT_PLACEHOLDER_PIL_IMAGE = Image.new('RGB', (300, 400), color=(128, 128, 128))  # A grey PIL placeholder

def load_pil_image_from_url(url: str | None) -> Image.Image:
    if url:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # print(f"Attempting to download image from: {url}") # Debug
            response = requests.get(url, stream=True, timeout=10, headers=headers)
            response.raise_for_status()  # Will raise an HTTPError for bad responses (4XX or 5XX)

            if not response.content:  # Check if content is empty
                print(f"Downloaded image from {url} is empty.")
                return DEFAULT_PLACEHOLDER_PIL_IMAGE

            img = Image.open(BytesIO(response.content))
            return img.convert("RGB")  # Convert to RGB to ensure compatibility
        except requests.exceptions.Timeout:
            print(f"Timeout when trying to download image from {url}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image from {url}: {e}")
        except IOError as e:  # PIL specific error
            print(f"Error opening image from {url} (PIL error): {e}")
        except Exception as e:
            print(f"An unexpected error occurred while loading image from {url}: {e}")
    return DEFAULT_PLACEHOLDER_PIL_IMAGE