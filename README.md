---
title: Aware NPC chat
emoji: 💬💡
colorFrom: indigo
colorTo: gray
sdk: gradio
python_version: 3.13
sdk_version: 5.31.0
app_file: src/app.py
pinned: false
short_description: A chat interface with an NPC aware of the world it lives in
tags:
  - agent-demo-track
---

# Chat with aware NPCs 

I love roleplaying and AI Agent may bring a whole new experience to chatting in games.

I want to build an AI Agent system that takes allow NPCs (Non Player Characters) to talk with you 
according to their own knowledge of the world they live in.

## Program
- [x] **Prerequisites:**
  - [x] Build a knowledge base (characters, places, events, objects)
  - [x] Build a simple and effective chat interface
  - [x] Basic agents to retrieve useful information and converse

- [ ] **Iterate to improve quality:**
  - [x] Improve the agent system, allow for personalization of the responses
  - [x] Integrate an emotional dimension into the responses
  - [x] Integrate a notion of willingness to answer
  - [ ] Grade the level of accessible knowledge

- [ ] **Bonus, not everything can be done:**
  - [ ] Generate alternative images translating the character's emotions with each response
  - [ ] An interface "behind the scenes of the chat," to visualize the work of the agents in the background
  - [ ] Generalize the process of building the knowledge base

## Install the project

Requires Python 3.13 or higher.

Install steps, _run_ refers to command lines in your terminal :
1. Clone the GitHub project
2. You might need to download [Git LFS](https://git-lfs.com/) in order to access the static large files. Then run `git lfs install` and finally `git lfs pull`.
3. [Create a virtual environment (recommended)](https://docs.python.org/3/library/venv.html)
4. [Install `uv` dependency manager](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) _e.g._ run `pip install pipx` then `pipx install uv` in a terminal
5. Run `uv sync` then `uv pip install -e .`
6. Set up your secrets (like HF_read_token), see example list in the `.example.env` file.
7. Run the app with `uv run src/app.py`

## Build a knowledge base from a fandom website

Download the XML file of the Fandom website :

```python
from knowledge_base.utils.downloader import download_file, fetch_page_content, get_xml_dump_url
from knowledge_base.utils.url import get_fandom_statistics_page_url

XML_PATH = r"....\asimov_fandom_dump.xml"

fandom_url = "https://asimov.fandom.com/wiki/"
statistics_url = get_fandom_statistics_page_url(fandom_url)
statistics_page_content = fetch_page_content(statistics_url)
xml_dump_url = get_xml_dump_url(statistics_page_content)

xml_file = download_file(xml_dump_url, output_path=XML_PATH)
```

From xml dump to knowledge base :
```python
from knowledge_base.models.knowledge_base import KnowledgeBase
from knowledge_base.parser.fandom.bridge_site_to_kb import populate_entities, populate_relationships
from knowledge_base.parser.fandom.parse_dump import fandom_xml_parse

XML_PATH = r"....\asimov_fandom_dump.xml"  # <= Same as previous code blob
KB_PATH = r"....\kb_asimov.json"

fandom_site_content = fandom_xml_parse(XML_PATH)

kb = KnowledgeBase()
populate_entities(fandom_site_content, kb)
populate_relationships(fandom_site_content, kb)
kb.save_kb(KB_PATH, compress=True)  # <= Compressing automatically add the .gz extension
```