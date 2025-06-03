from knowledge_base.utils.regex import extract_fandom_categories

def test_extract_categories():
    """Test with known categories"""
    xml_content_1 = """
    Some content here [[Category:Science]] and some more content [[Category:Fiction]].
    """
    assert extract_fandom_categories(xml_content_1) == ["Science", "Fiction"]

def test_no_categories():
    """Test with no categories"""
    xml_content_2 = """
    Some content here with no categories.
    """
    assert extract_fandom_categories(xml_content_2) == []

def test_empty_content():
    """Test with empty content"""
    xml_content_3 = ""
    assert extract_fandom_categories(xml_content_3) == []

def test_multiple_categories():
    # Test case 4: Test with multiple categories
    xml_content_4 = """
    [[Category:Adventure]] [[Category:Science]] [[Category:Fiction]].
    """
    assert set(extract_fandom_categories(xml_content_4)) == {"Adventure", "Science", "Fiction"}

def test_special_characters():
    """Test with special characters in category names"""
    xml_content_5 = """
    Some content with [[Category:Science-Fiction]] and [[Category:Adventure_Time]].
    """
    assert extract_fandom_categories(xml_content_5) == ["Science-Fiction", "Adventure_Time"]
