import os
from dotenv import load_dotenv

from smolagents import InferenceClientModel, FinalAnswerTool

from agents.personalized_agent import PersonalizedAgent
from agents.prompt_templates.emotional_chatting import EmotionalChattingParams
from knowledge_base.models.entities import Character
from knowledge_base.models.knowledge_base import KnowledgeBase
from tools.kb_query import get_character_infos, get_all_relationships

# Load the .env file
load_dotenv()
hf_token = os.getenv("HF_TOKEN")

# Choice of the model
model_name = "mistralai/Mistral-7B-Instruct-v0.3"
llm = InferenceClientModel(
    model_id=model_name,
    temperature=0.7,
    max_tokens=1000,
    token=hf_token,
    custom_role_conversions=None,
)

# response = llm([{"role": "user", "content": "Explain quantum mechanics in simple terms."}])

empty_character_kwargs = dict(
    aliases=[],
    abilities=[],
    occupation=None,
    species=None,
    physical_description={},
    personality_traits=[]
)

chatting_agent = PersonalizedAgent(
    model=llm,
    # add your tools here (don't remove FinalAnswerTool())
    additional_authorized_imports=[],
    tools=[FinalAnswerTool(), get_character_infos, get_all_relationships],
    max_steps=4,
    grammar=None,
    planning_interval=5,
    name="Character_Chat_Agent",
    description="The Agent is a character in a story."
                "His personnality and background are defined by a character sheet."
                "It is able to answer questions and provide explanations when asked.",
    prompt_templates=EmotionalChattingParams.prompt_template,
    # Empty state at init is a workaround. I did not want to use time to fix this minor issue
    # It allows the initial system prompt to init
    state={
        "kb": KnowledgeBase(),
        "character_name": "Test character",
        "character": Character(name="Test character", **empty_character_kwargs),
    },
)