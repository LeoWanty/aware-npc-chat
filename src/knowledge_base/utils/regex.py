import json
import re
from typing import List

def extract_fandom_categories(text: str) -> List[str]:
    """
    Extracts categories from a fandom page XML content.

    This function uses regular expressions to find and extract categories
    from the text issued from XML content. The categories are identified by the pattern
    [[Category:CategoryName]].

    Parameters:
    text (str): The text issued from XML content of the fandom page as a string.

    Returns:
    List[str]: A list of category names found in the XML content.
    """
    # Regular expression pattern to match categories
    pattern = r"\[\[Category:([^\]]+)\]\]"

    matches = re.findall(pattern, text)
    return matches


def extract_fandom_links(text):
    """
    Extracts wiki links from a given text.

    This function uses regular expressions to find all wiki links in the text.
    Wiki links are typically enclosed in double brackets [[...]].

    Parameters:
    text (str): The text from which to extract wiki links.

    Returns:
    list: A list of extracted wiki links.
    """
    # Regular expression pattern to match wiki links
    pattern = r"\[\[([^\]]+)\]\]"

    # Find all matches of the pattern in the text
    matches = re.findall(pattern, text)

    # Further processing to separate the link text and display text if necessary
    links = []
    for match in matches:
        # Split on the pipe character to separate the link from the display text
        link_parts = match.split("|")
        links.append(link_parts[0])

    return links


def extract_sentences_with_keyword(text:str, keyword:str):
    """
    Extracts sentences containing a specific keyword from a given text.

    This function uses regular expressions to split the text into sentences
    and then filters those sentences to only include ones containing the keyword.

    Parameters:
    text (str): The text from which to extract sentences.
    keyword (str): The keyword that sentences must contain.

    Returns:
    str: A single string composed of sentences that contain the keyword, joined together.
    """
    # Regular expression pattern to split text into sentences
    # This pattern is a simple approximation and may need adjustments
    sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'

    # Split the text into sentences
    sentences = re.split(sentence_pattern, text)

    # Filter sentences to only include those containing the keyword
    filtered_sentences = [sentence for sentence in sentences if keyword.lower() in sentence.lower()]

    # Join the filtered sentences into a single string
    result = ' '.join(filtered_sentences)

    return result


def extract_json_from_text(text):
    # Regular expression to find JSON code blocks in Markdown
    pattern = r"```json\n([\s\S]+?)```"
    json_blobs = re.findall(pattern, text)

    parsed_json_blobs = []
    for blob in json_blobs:
        try:
            # Parse the JSON blob into a Python dictionary
            parsed_data = json.loads(blob)
            parsed_json_blobs.append(parsed_data)
        except json.JSONDecodeError as e:
            # Handle any errors in JSON decoding
            print(f"An error occurred while parsing a JSON blob: {e}")

    return parsed_json_blobs