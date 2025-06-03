import tempfile
from pathlib import Path

from knowledge_base.models.knowledge_base import KnowledgeBase
from knowledge_base.parser.fandom.bridge_site_to_kb import _extract_entity_from_page, populate_entities, \
    extract_relationships_from_page, populate_relationships
from knowledge_base.parser.fandom.models import FandomSiteContent
from knowledge_base.parser.fandom.parse_dump import fandom_xml_parse
from knowledge_base.utils.archive_handler import extract_7z
from knowledge_base.utils.downloader import fetch_page_content, get_xml_dump_url, download_file


def from_fandom(fandom_url) -> KnowledgeBase:
    fandom_stat_page_content = fetch_page_content(fandom_url)
    dump_url = get_xml_dump_url(fandom_stat_page_content)

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_dir_path = Path(tmp_dir)
        download_path = temp_dir_path / "fandom_archive.xml.7z"
        extracted_file_path = temp_dir_path / "fandom_extracted"
        download_file(dump_url, output_path=download_path)
        extract_7z(download_path, extracted_file_path)

        xml_path = extracted_file_path / "fandom_archive.xml"
        fandom_site_content = fandom_xml_parse(xml_path)

        _extract_entity_from_page(fandom_site_content)
        populate_entities()
        # extract_relationships_from_page()
        # populate_relationships()

    return ...