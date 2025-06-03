import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from pydantic import ValidationError
from typing import Optional, Dict, Any

from knowledge_base.parser.fandom.models import FandomSiteContent, SiteInfo, Page, Revision, Contributor, Text


def _get_element_text(element: Optional[ET.Element]) -> Optional[str]:
    return element.text if element is not None else None


def _get_element_attr(element: Optional[ET.Element], attr_name: str) -> Optional[str]:
    return element.get(attr_name) if element is not None else None


def fandom_xml_parse(xml_file_path: Path | str) -> FandomSiteContent:
    """
    Parses a MediaWiki XML dump file iteratively and populates Pydantic models.

    Args:
        xml_file_path: Path to the XML dump file.

    Returns:
        A KnowledgeBase object populated with data from the dump.
    """
    kb = FandomSiteContent()
    current_page_data: Optional[Dict[str, Any]] = None
    current_revision_data: Optional[Dict[str, Any]] = None
    current_contributor_data: Optional[Dict[str, Any]] = None
    current_text_data: Optional[Dict[str, Any]] = None

    # For handling namespaces in siteinfo
    current_namespaces: Dict[int, str] = {}

    # Path tracking to know where we are in the XML tree
    path: list[str] = []

    print(f"Starting XML parsing for: {xml_file_path}")
    iter_events = ET.iterparse(xml_file_path, events=('start', 'end'))

    for event, elem in iter_events:
        tag_name = elem.tag.split('}')[-1]  # Strip namespace if present

        if event == 'start':
            path.append(tag_name)
            # Initialize data dicts when starting complex elements
            if tag_name == 'page':
                current_page_data = {"revisions": []}
            elif tag_name == 'revision':
                current_revision_data = {}
            elif tag_name == 'contributor' and 'revision' in path:  # Ensure contributor is within revision
                current_contributor_data = {}
            elif tag_name == 'text' and 'revision' in path:  # Ensure text is within revision
                current_text_data = {
                    "bytes": _get_element_attr(elem, "bytes"),
                    "sha1": _get_element_attr(elem, "sha1"),
                    "deleted": "deleted" if _get_element_attr(elem, "deleted") == "deleted" else None,
                    "content": None  # Will be filled at 'end' event for text
                }
            elif tag_name == 'siteinfo' and not kb.siteinfo:  # Initialize siteinfo only once
                kb.siteinfo = SiteInfo()
            elif tag_name == 'namespaces' and 'siteinfo' in path:
                current_namespaces = {}  # Prepare to collect namespaces


        elif event == 'end':
            path.pop()

            # SiteInfo processing
            if tag_name == 'sitename' and 'siteinfo' in path and kb.siteinfo:
                kb.siteinfo.sitename = _get_element_text(elem)
            elif tag_name == 'dbname' and 'siteinfo' in path and kb.siteinfo:
                kb.siteinfo.dbname = _get_element_text(elem)
            elif tag_name == 'base' and 'siteinfo' in path and kb.siteinfo:
                kb.siteinfo.base = _get_element_text(elem)  # Pydantic will validate HttpUrl
            elif tag_name == 'generator' and 'siteinfo' in path and kb.siteinfo:
                kb.siteinfo.generator = _get_element_text(elem)
            elif tag_name == 'case' and 'siteinfo' in path and kb.siteinfo:
                kb.siteinfo.case = _get_element_text(elem)
            elif tag_name == 'namespace' and 'namespaces' in path and 'siteinfo' in path and kb.siteinfo:
                ns_key = _get_element_attr(elem, "key")
                ns_text = _get_element_text(elem)
                if ns_key is not None and ns_text is not None:
                    try:
                        current_namespaces[int(ns_key)] = ns_text
                    except ValueError:
                        print(f"Warning: Could not parse namespace key '{ns_key}' as integer.")
            elif tag_name == 'namespaces' and 'siteinfo' in path and kb.siteinfo:
                kb.siteinfo.namespaces = current_namespaces
                current_namespaces = {}  # Reset for safety, though not strictly needed here

            # Page processing
            elif tag_name == 'title' and 'page' in path and current_page_data is not None:
                current_page_data['title'] = _get_element_text(elem)
            elif tag_name == 'ns' and 'page' in path and current_page_data is not None:
                current_page_data['ns'] = _get_element_text(elem)
            elif tag_name == 'id' and 'page' in path and current_page_data is not None and 'revision' not in path:  # Page ID, not revision ID
                current_page_data['id'] = _get_element_text(elem)
            elif tag_name == 'redirect' and 'page' in path and current_page_data is not None:
                current_page_data['redirect_title'] = _get_element_attr(elem, "title")
            elif tag_name == 'restrictions' and 'page' in path and current_page_data is not None:
                if 'restrictions' not in current_page_data:
                    current_page_data['restrictions'] = []
                if _get_element_text(elem):
                    current_page_data['restrictions'].append(_get_element_text(elem))

            # Revision processing
            elif tag_name == 'id' and 'revision' in path and current_revision_data is not None:
                current_revision_data['id'] = _get_element_text(elem)
            elif tag_name == 'parentid' and 'revision' in path and current_revision_data is not None:
                current_revision_data['parentid'] = _get_element_text(elem)
            elif tag_name == 'timestamp' and 'revision' in path and current_revision_data is not None:
                ts_text = _get_element_text(elem)
                if ts_text:
                    try:
                        # MediaWiki timestamp format: 2001-01-15T13:42:29Z
                        current_revision_data['timestamp'] = datetime.fromisoformat(ts_text.replace('Z', '+00:00'))
                    except ValueError:
                        print(f"Warning: Could not parse timestamp '{ts_text}'. Skipping revision field.")
            elif tag_name == 'minor' and 'revision' in path and current_revision_data is not None:
                current_revision_data['minor'] = True  # Presence of tag means true
            elif tag_name == 'comment' and 'revision' in path and current_revision_data is not None:
                current_revision_data['comment'] = _get_element_text(elem)
            elif tag_name == 'model' and 'revision' in path and current_revision_data is not None:
                current_revision_data['model'] = _get_element_text(elem)
            elif tag_name == 'format' and 'revision' in path and current_revision_data is not None:
                current_revision_data['format'] = _get_element_text(elem)
            elif tag_name == 'sha1' and 'revision' in path and current_revision_data is not None and 'text' not in path:  # Revision's sha1
                current_revision_data['sha1'] = _get_element_text(elem)


            # Contributor processing (within revision)
            elif tag_name == 'username' and 'contributor' in path and current_contributor_data is not None:
                current_contributor_data['username'] = _get_element_text(elem)
            elif tag_name == 'id' and 'contributor' in path and current_contributor_data is not None:
                current_contributor_data['id'] = _get_element_text(elem)
            elif tag_name == 'ip' and 'contributor' in path and current_contributor_data is not None:
                current_contributor_data['ip'] = _get_element_text(elem)
            elif tag_name == 'contributor' and 'revision' in path and current_revision_data is not None and current_contributor_data is not None:
                try:
                    current_revision_data['contributor'] = Contributor(**current_contributor_data)
                except ValidationError as e:
                    print(
                        f"Warning: Contributor validation error for revision {current_revision_data.get('id')}: {e}")
                current_contributor_data = None  # Reset

            # Text processing (within revision)
            elif tag_name == 'text' and 'revision' in path and current_revision_data is not None and current_text_data is not None:
                current_text_data["content"] = _get_element_text(elem)  # Get the actual text content
                # Bytes and sha1 for text are handled at 'start' of text element via attributes
                # 'deleted' attribute also handled at 'start'
                try:
                    current_revision_data['text'] = Text(**current_text_data)
                except ValidationError as e:
                    print(f"Warning: Text validation error for revision {current_revision_data.get('id')}: {e}")
                current_text_data = None  # Reset

            # Assembling Revision
            elif tag_name == 'revision' and 'page' in path and current_page_data is not None and current_revision_data is not None:
                # Ensure required fields for Revision are present before creating model
                if 'id' in current_revision_data and 'timestamp' in current_revision_data \
                        and 'contributor' in current_revision_data and 'text' in current_revision_data:
                    try:
                        # Set default for minor if not present
                        current_revision_data.setdefault('minor', False)
                        revision = Revision(**current_revision_data)
                        current_page_data["revisions"].append(revision)
                    except ValidationError as e:
                        print(
                            f"Warning: Revision validation error for page {current_page_data.get('title')}: {e}. Revision data: {current_revision_data}")
                else:
                    print(f"Warning: Skipping revision due to missing critical data. Data: {current_revision_data}")
                current_revision_data = None  # Reset

            # Assembling Page
            elif tag_name == 'page':
                if current_page_data is not None:
                    # Ensure required fields for Page are present
                    if 'title' in current_page_data and 'ns' in current_page_data and 'id' in current_page_data:
                        try:
                            page = Page(**current_page_data)
                            kb.pages.append(page)
                        except ValidationError as e:
                            print(f"Warning: Page validation error: {e}. Page data: {current_page_data}")
                    else:
                        print(f"Warning: Skipping page due to missing critical data. Data: {current_page_data}")
                current_page_data = None  # Reset

            # Clear element from memory to save space, crucial for large files
            if elem.tag not in ['mediawiki', 'siteinfo', 'page', 'revision', 'contributor', 'text',
                                'namespaces']:  # Avoid clearing containers too early
                # More aggressive clearing might be needed if memory is still an issue
                # Need to be careful not to clear parent elements before children are processed
                pass  # Delay clearing until parent is done, or manage path carefully

            # A common strategy for iterparse is to clear children after the parent's 'end' event.
            # For example, after a 'page' ends, all its children ('revision', etc.) can be cleared.
            # elem.clear() should be called on the element that just *ended*.
            # It also clears its children.
            # Clearing elements that are parents for current data (like current_page_data) before they are used
            # would be problematic.
            # The list of elements to clear should be those that are fully processed and their data extracted.
            # Example: clear 'revision' when its 'end' event is processed and data is in current_revision_data.
            # However, ET iterparse processes children first. So when 'revision' ends, its children (<text>, <contributor>)
            # have already ended and could have been cleared.
            # The most important thing is to clear the element that just finished `elem.clear()`.
            # This also clears its text and attributes from memory.
            # If the element has children, they are also cleared.
            # This is generally safe if data is extracted to Python dicts/objects.

            # If we are at the end of a major element like 'page' or 'siteinfo', clear it.
            # For other elements, if they are not parents in the 'path' of current data dicts, clear them.
            # This is a bit tricky. A simpler approach: clear every element at its 'end' event.
            # This is safe because we extract data into our dicts.
            elem.clear()
            # And remove from parent to allow parent to be garbage collected sooner, if possible.
            # This part is more complex with iterparse; elem.clear() is the main tool.
            # If using lxml, it has more advanced options for this.

    print(f"Finished XML parsing. Found {len(kb.pages)} pages.")
    if kb.siteinfo:
        print(f"SiteInfo: {kb.siteinfo.sitename if kb.siteinfo else 'Not found'}")
    return kb
