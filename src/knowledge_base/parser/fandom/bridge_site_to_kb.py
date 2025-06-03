"""
Handles the extraction of entities and relationships from Fandom XML page data
to populate a KnowledgeBase.

This module provides functions to:
- Identify entity types from page content using keyword matching.
- Create entity objects with basic information.
- Extract relationships between entities based on wikitext links.
- Populate a KnowledgeBase instance with these entities and relationships.
"""
import re
from typing import Optional, Dict
from uuid import UUID

from knowledge_base.logger import logger
from knowledge_base.models.entities import Entity, Character, Place, Event, SpecialObject
from knowledge_base.models.knowledge_base import KnowledgeBase
from knowledge_base.models.relationships import Relationship, RELATIONSHIP_TYPE_MISC
from knowledge_base.parser.fandom.models import Page, FandomSiteContent
from knowledge_base.utils.regex import extract_fandom_categories

# ENTITY_TYPE_MAP maps entity type strings (as determined by DEFAULT_CATEGORY_KEYWORDS)
# to their corresponding Pydantic model classes from .models.entities.
CAT_TO_ENTITY_MAPPING: Dict[str, Entity] = {
    "Characters": Character,
    " Characters" : Character,
    "Nemesis": Character,
    "Places": Place,
    "Planets": Place,
    "Cities": Place,
    "Events": Event,
    "Calendar": Event,
    "SpecialObject": SpecialObject
}

def get_entity_args(entity_class: Entity, page: Page):
    """
    WIP : should be an agent that extracts the entity args from the page

    for now, it's a dummy function that returns a dict with the common args.
    """
    wikitext = page.revisions[-1].text.content

    common_args = dict(
        name = page.title,
        description = (wikitext[:500] + '...') if len(wikitext) > 500 else wikitext,
    )

    if entity_class == Character:
        specific_args = dict(
            aliases= [],
            abilities = [],
            occupation = None,
            species = None,
            physical_description = {},
            personality_traits = []
        )
    elif entity_class == Place:
        specific_args = dict(location_type=None, coordinates=None)
    elif entity_class == Event:
        specific_args = dict(event_type=None)
    elif entity_class == SpecialObject:
        specific_args = dict(object_type=None)
    else:
        logger.error(f"Entity class {entity_class!r} not handled for specific instantiation for page: {page.title}")
        return None
    return {**common_args, **specific_args}


def extract_entity_from_page(
        page: Page,
        category_to_entity_mapping: Optional[Dict[str, Entity]] = None
) -> Optional[Entity]:
    """
    Extracts entity information from a single Fandom `Page` object.

    The function determines the entity's type (e.g., Character, Place) by searching
    for predefined keywords or patterns within the page's latest revision text.
    If a known entity type is identified, an entity object is instantiated. The entity's
    name is taken from the page title, and a basic description is extracted from the
    initial part of the wikitext.

    Args:
        page: The `Page` object, typically parsed from a Fandom XML dump,
          containing the title, revisions, and other metadata.
        category_to_entity_mapping: A dictionary mapping entity type names (e.g., "Character")
           to a list of regex patterns. These patterns are searched for within
           the page's wikitext to determine its entity type.

    Returns:
        The newly created `Entity` if the process is successful.
        Returns `None` if no entity type can be determined,
        if the page has no revisions or text content,
        or if any error occurs during entity instantiation.
    """
    if category_to_entity_mapping is None:
        category_to_entity_mapping = CAT_TO_ENTITY_MAPPING

    if not page.revisions:
        logger.warning(f"Page '{page.title}' has no revisions. Cannot extract entity.")
        return None

    latest_revision = page.revisions[-1]  # Assuming revisions are ordered
    if not latest_revision.text or not latest_revision.text.content:
        logger.warning(f"Latest revision for page '{page.title}' has no text content. Cannot extract entity.")
        return None

    wikitext = latest_revision.text.content
    page_categories = extract_fandom_categories(wikitext)
    entity_class: Optional[Entity] = None
    for c in page_categories:
        entity_class = category_to_entity_mapping.get(c)
        if entity_class:
            break  # Stop when a first category helped to fix entity type

    if not entity_class:
        logger.warning(f"Could not determine entity type for page: {page.title}")
        return None

    entity_args = get_entity_args(entity_class, page)
    return entity_class.model_validate(entity_args)


def populate_entities(
        site_content: FandomSiteContent,
        kb: KnowledgeBase,
        category_keywords: Optional[Dict[str, Entity]] = None
) -> None:
    """
    Populates the given `KnowledgeBase` with entities extracted from all pages
    within the `FandomSiteContent` object.

    This function iterates over each `Page` in `site_content.pages`, calling
    `extract_entity_from_page` for each one to determine if it represents a
    known entity type and, if so, to create and add it to the `KnowledgeBase`.

    Args:
        site_content: A `FandomSiteContent` object, which contains a list of `Page`
                      objects parsed from a Fandom XML dump.
        kb: The `KnowledgeBase` instance to be populated with extracted entities.
            This function has the side effect of modifying this `KnowledgeBase`.
        category_keywords: Optional. A dictionary of category keywords to guide entity
                           type detection, passed down to `extract_entity_from_page`.
                           If `None`, `CAT_TO_ENTITY_MAPPING` will be used by
                           `extract_entity_from_page`.

    Returns:
        None. The KnowledgeBase is modified in-place with new entities.
    """
    if not site_content or not site_content.pages:
        logger.warning("No pages found in site_content. Nothing to populate.")

    logger.info(f"Starting entity population from {len(site_content.pages)} pages...")

    entity_added_count = 0
    for page in site_content.pages:
        logger.debug(f"Processing page: {page.title}")
        entity = extract_entity_from_page(page, category_keywords)

        if entity:
            kb.add_entity(entity)
            entity_added_count += 1
            logger.info(f"Successfully created entity '{page.title}' (ID: {entity})")
        else:
            # Warning already logged by extract_entity_from_page if type not determined or other issues
            logger.info(f"Could not create entity for page: '{page.title}' (see previous warnings for details).")

    logger.info(f"Entity population complete. Created {entity_added_count} entities.")


def extract_relationships_from_page(
        page: Page,
        kb: KnowledgeBase
) -> None:
    """
    Extracts relationships from a single Fandom `Page` object based on wikitext links
    (e.g., `[[Target Page]]`) and adds these relationships to the `KnowledgeBase`.

    This function first identifies the source entity corresponding to the given `page`
    using the `page_to_entity_map`. It then scans the wikitext of the page's latest
    revision for standard MediaWiki links. If a linked page title corresponds to another
    known entity in the `page_to_entity_map`, a "LINKS_TO" relationship is created
    between the source entity and the target entity and added to the `KnowledgeBase`.

    Args:
        page: The `Page` object from which to extract relationships. This page is
              treated as the source of the potential outgoing links.
        kb: The `KnowledgeBase` instance to which new relationships will be added.
            This function has the side effect of modifying this `KnowledgeBase`.
    """
    source_entity = kb.get_entity_by_name(page.title)
    if not source_entity:
        logger.warning(f"Page '{page.title}' (ID: {page.id}) not in entity map. Skipping relationship extraction.")
        return

    if not page.revisions:
        logger.warning(f"No revisions for page '{page.title}'. Skipping relationship extraction.")
        return
    latest_revision = page.revisions[-1]
    if not latest_revision.text or not latest_revision.text.content:
        logger.warning(f"No text content in latest revision for page '{page.title}'. Skipping relationship extraction.")
        return
    wikitext = latest_revision.text.content

    # Regex to find standard MediaWiki links.
    # - `\[\[`: Matches the opening double square brackets.
    # - `([^\]|#]+)`: This is the first capturing group. It captures the main page title.
    #   - `[^\]|#]`: Matches any character that is NOT a closing square bracket `]`, a pipe `|`, or a hash `#`.
    #   - `+`: Matches one or more of the preceding characters.
    # - `(?:\|[^\]]+)?`: This is an optional non-capturing group for the display text (alias).
    #   - `\|`: Matches the pipe character.
    #   - `[^\]]+`: Matches any character that is NOT a closing square bracket, one or more times.
    #   - `?`: Makes this entire group optional.
    # - `(?:#[^\]]+)?`: This is an optional non-capturing group for section links (fragments).
    #   - `#`: Matches the hash character.
    #   - `[^\]]+`: Matches any character that is NOT a closing square bracket, one or more times.
    #   - `?`: Makes this entire group optional.
    # - `\]\]`: Matches the closing double square brackets.
    # The regex aims to extract only the canonical page title, stripping away aliases and section links.
    link_regex = r"\[\[([^\]|#]+)(?:\|[^\]]+)?(?:#[^\]]+)?\]\]"

    try:
        # re.findall returns a list of all non-overlapping matches of the pattern in the string.
        # If the pattern includes one capturing group, the result is a list of strings (the captured groups).
        linked_page_titles_matches = re.findall(link_regex, wikitext)
    except Exception as e:
        logger.error(f"Error during regex link finding for page '{page.title}': {e}")
        return

    if not linked_page_titles_matches:
        # This can be very verbose if logged for every page without links.
        # logger.debug(f"No links found in page '{page.title}'.")
        return

    # logger.debug(f"Found {len(linked_page_titles_matches)} potential links in page '{page.title}'.")

    for target_page_title_str in linked_page_titles_matches:
        target_page_title = target_page_title_str.strip()

        if not target_page_title:  # Skip if the captured title is empty after stripping
            continue

        if target_page_title == page.title:  # Avoid self-loops
            continue

        target_entity = page_to_entity_map.get(target_page_title)

        if target_entity:
            try:
                relationship = Relationship(
                    source_entity_id=source_entity,
                    target_entity_id=target_entity,
                    relationship_type=RELATIONSHIP_TYPE_MISC,
                    description=f"Page '{page.title}' links to page '{target_page_title}'."
                )
                kb.add_relationship(relationship)
                logger.info(
                    f"Created relationship: '{page.title}' -> '{target_page_title}' (Type: {RELATIONSHIP_TYPE_MISC})")
            except Exception as e:  # Catch potential Pydantic validation errors or other issues
                logger.error(f"Error creating relationship '{page.title}' -> '{target_page_title}': {e}")
        else:
            # This can also be verbose. Consider logging at DEBUG level or only if specifically needed.
            logger.debug(
                f"Linked page '{target_page_title}' from '{page.title}' not found in entity map. No relationship created.")


def populate_relationships(
        site_content: FandomSiteContent,
        kb: KnowledgeBase,
        page_to_entity_map: Dict[str, UUID]
) -> None:
    """
    Populates the `KnowledgeBase` with relationships by iterating through all pages
    in `site_content` and extracting links.

    For each page in the `site_content`, this function calls
    `extract_relationships_from_page` to find links to other pages and create
    corresponding "LINKS_TO" relationships in the `KnowledgeBase`.

    Args:
        site_content: A `FandomSiteContent` object containing all pages from the XML dump.
        kb: The `KnowledgeBase` instance to be populated with relationships.
            This function has the side effect of modifying this `KnowledgeBase`.
        page_to_entity_map: A dictionary mapping page titles (str) to entity `UUID`s.
                            This is passed to `extract_relationships_from_page` and is
                            essential for resolving linked pages to their actual entity IDs.
    """
    if not site_content or not site_content.pages:
        logger.warning("No pages found in site_content. Skipping relationship population.")
        return

    if not page_to_entity_map:
        logger.warning("Entity map (page_title_to_entity_uuid) is empty. "
                       "Relationships cannot be formed. Skipping relationship population.")
        return

    logger.info(f"Starting relationship population for {len(site_content.pages)} pages...")

    processed_pages = 0
    for page_obj in site_content.pages:
        # logger.debug(f"Extracting relationships from page: '{page_obj.title}'") # Optional: for verbose logging
        try:
            # extract_relationships_from_page uses the module-level logger
            extract_relationships_from_page(page_obj, kb, page_to_entity_map)
            processed_pages += 1
        except Exception as e:
            logger.error(f"Unexpected error processing relationships for page '{page_obj.title}': {e}", exc_info=True)

    logger.info(f"Relationship population attempt finished. Processed {processed_pages} pages.")
