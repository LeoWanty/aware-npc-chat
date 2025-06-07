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
  - [ ] Improve the agent system, particularly by grading the level of accessible knowledge
  - [ ] Integrate an emotional dimension into the responses

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
