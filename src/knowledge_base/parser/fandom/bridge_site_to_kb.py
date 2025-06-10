"""
Handles the extraction of entities and relationships from Fandom XML page data
to populate a KnowledgeBase.

This module provides functions to:
- Identify entity types from page content using keyword matching.
- Create entity objects with basic information.
- Extract relationships between entities based on wikitext links.
- Populate a KnowledgeBase instance with these entities and relationships.
"""
from typing import Optional, Dict, List

from knowledge_base.logger import logger
from knowledge_base.models.entities import Entity, Character, Place, Event, SpecialObject
from knowledge_base.models.knowledge_base import KnowledgeBase
from knowledge_base.models.relationships import Relationship, RELATIONSHIP_TYPE_MISC
from knowledge_base.parser.fandom.models import Page, FandomSiteContent
from knowledge_base.utils.regex import extract_fandom_categories, extract_fandom_links, extract_sentences_with_keyword, \
    extract_json_from_text

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


def _extract_info_through_llm(text: str, target_class, field_to_fill: list[str]):
    import os
    from dotenv import load_dotenv

    from smolagents import InferenceClientModel

    # Load the .env file
    load_dotenv()
    hf_token = os.getenv("HF_TOKEN")

    # Choice of the model
    model_name = "mistralai/Mistral-7B-Instruct-v0.3"
    llm = InferenceClientModel(
        model_id=model_name,
        temperature=0.7,
        # max_tokens=1000,
        token=hf_token,
        custom_role_conversions=None,
    )

    fields_pretty_printable = "\n".join([
        f"  {field} : {field_info}"
        for field, field_info in target_class.model_fields.items()
        if field in field_to_fill
    ])
    fields_to_complete = "\n".join([
        f"\t{field} : ,"
        for field in target_class.model_fields
        if field in field_to_fill
    ])

    message = f"""
You are a helpful assistant that extracts information from the following text:
```json
{{
{fields_pretty_printable}
}}
```

In a valid JSON code blob, replace the FieldInfo with actual information extracted from the text. Keep it short.
Keep the default if no relevant information is found.

Here is the text:
{text}

The output should be in the form of a valid JSON code blob.
Use default values if no relevant information is found.

DON'T DO THOSE JSON common mistakes:
- Missing or mismatched brackets ({{}}) or square brackets ([]).
- Trailing commas at the end of objects or arrays.
- Missing or mismatched quotes around keys or string values. Use single quotes (') only instead of double quotes (").
- Invalid characters or escape sequences.
- Comments in JSON (JSON does not support comments).

You just have to copy and fill a valid JSON code blob from below.
Fill with actual information extracted from the text. Keep it short.
Keep the default if no relevant information is found :
```json
{{
{fields_to_complete}
}}
```<end_code>
    """
    return llm([{"role": "user", "content": message}])


def get_entity_args(entity_class: Entity, page: Page, fill_with_llm):
    """
    WIP : should be an agent that extracts the entity args from the page

    for now, it's a dummy function that returns a dict with the common args.
    """
    wikitext = page.revisions[-1].text.content

    common_args = dict(
        name = page.title,
        description = wikitext,
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

    if fill_with_llm:
        args_to_fill = list(specific_args.keys()) if specific_args else []
        llm_response = _extract_info_through_llm(wikitext, entity_class, args_to_fill)
        json_blobs = extract_json_from_text(llm_response.content)
        last_blob = json_blobs[-1]  # Should be the last one if multiple blobs are produced. See prompt from _extract_info_through_llm.
        # Verify that keys are the expected one (avoid hallucinations)
        to_update = {field: value for field, value in last_blob.items() if field in specific_args}
        specific_args.update(to_update)
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
) -> Optional[list[Relationship]]:
    """
    Extracts relationships from a single Fandom `Page` object based on wikitext links
    (e.g., `[[Target Page]]`) and adds these relationships to the `KnowledgeBase`.

    This function first identifies the source entity corresponding to the given `page`.
    It then scans the wikitext of the page's latest revision for standard MediaWiki links.
    If a linked page title corresponds to another known entity in the `page_to_entity_map`,
    a relationship is created between the source entity and the target entity
    and added to the `KnowledgeBase`.

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

    links = extract_fandom_links(wikitext)
    logger.debug(f"Found {len(links)} potential links in page '{page.title}'.")

    # If not mapped, chances are the content is not relevant.
    # Better work on Entity recognition than tweak the filter there
    # AND Avoid self-loops
    # AND Remove duplicates references
    kept_links = [
        link
        for link in set(links)
        if link in kb.map_entity_name_to_id or link.strip() == page.title
    ]

    relationships_args = get_relationships_args(
        text=wikitext,
        source_entity_name=page.title,
        targets_entity_name=kept_links,
        kb=kb
    )
    return [Relationship.model_validate(args) for args in relationships_args]


def get_relationships_args(
        text: str,
        source_entity_name: str,
        targets_entity_name: List[str],
        kb: KnowledgeBase,
) -> list[dict]:
    return [
        dict(
        source_entity_id=kb.map_entity_name_to_id[source_entity_name],
        target_entity_id=kb.map_entity_name_to_id[target_name],
        # TODO : rework those later with agent
        relationship_type=RELATIONSHIP_TYPE_MISC,
        description=extract_sentences_with_keyword(text=text, keyword=target_name)
    )
        for target_name in targets_entity_name
    ]

def populate_relationships(
        site_content: FandomSiteContent,
        kb: KnowledgeBase,
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
    """
    if not site_content or not site_content.pages:
        logger.warning("No pages found in site_content. Skipping relationship population.")
        return

    logger.info(f"Starting relationship population for {len(site_content.pages)} pages...")

    processed_pages = 0
    for page in site_content.pages:
        if page.title not in kb.map_entity_name_to_id:
            continue  # No need to look at those pages as we would have no source for relationship
        logger.debug(f"Extracting relationships from page: '{page.title}'")
        try:
            relationships = extract_relationships_from_page(page=page, kb=kb)
            kb.add_relationships(relationships=relationships)
            processed_pages += 1
        except Exception as e:
            logger.error(f"Unexpected error processing relationships for page '{page.title}': {e}", exc_info=True)

    logger.info(f"Relationship population attempt finished. Processed {processed_pages} pages.")
