from smolagents import ToolCallingAgent, InferenceClientModel, FinalAnswerTool
import os
from dotenv import load_dotenv


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

chatting_agent = ToolCallingAgent(
    model=llm,
    tools=[FinalAnswerTool()],  # add your tools here (don't remove FinalAnswerTool())
    max_steps=3,
    grammar=None,
    planning_interval=None,
    name="Character_Chat_Agent",
    description="The Agent is a character in a story."
                "His personnality and background are defined by a character sheet."
                "It is able to answer questions and provide explanations when asked.",
    prompt_templates=None,
)