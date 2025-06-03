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

