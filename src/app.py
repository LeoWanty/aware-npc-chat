import gradio as gr
from PIL import Image

from config import SRC_PATH
from knowledge_base.models.knowledge_base import KnowledgeBase

from knowledge_base.utils.url import get_fandom_page_url
from tools.scraping import get_figure_html_from_fandom_page, load_pil_image_from_url

# Load the KnowledgeBase
DEFAULT_FANDOM_URL = 'https://asimov.fandom.com/wiki/'
DEFAULT_KB_PATH = SRC_PATH / 'static/kb_asimov.json'
kb = KnowledgeBase.from_json(DEFAULT_KB_PATH)

# Extract character names
character_names = [
    node_data.get('entity').name
    for node, node_data in kb.graph.nodes(data=True)
    if node_data.get('type') == 'Character'
]

# Placeholder for the agent's tool - This is a MOCK for the subtask's context.
# The actual tool will be provided by the agent's environment.
def get_character_image(character_name:str, base_url: str) -> Image:
    page_url = get_fandom_page_url(character_name, base_url)
    image_url = get_figure_html_from_fandom_page(page_url)
    return load_pil_image_from_url(image_url)

# Determine default values
if character_names:
    default_character_name = character_names[0]
    initial_pil_image_to_display = get_character_image(default_character_name, DEFAULT_FANDOM_URL)


def process_chat(message, current_chat_history, selected_character):
    """
    Processes a chat message by appending it to the current chat history and generating a
    simple echo response.

    Args:
    message (str): The user message to be processed.
    current_chat_history (list[dict[str, str]]): The existing chat history, where each entry
        contains a role ('user' or 'assistant') and its corresponding content.
    selected_character (str): The selected character to talk to

    Returns:
    tuple[list[dict[str, str]], list[dict[str, str]], str]: A tuple containing the updated chat
        history for chatbot display, the updated history for state management, and an empty string
        for the chat input textbox.
    """
    new_chat_history = list(current_chat_history)

    user_message_entry = {"role": "user", "content": message}
    bot_response_content = f"Echo: {message}"  # Simple echo response, to be updated later

    new_chat_history.append(user_message_entry)
    new_chat_history.append({"role": "assistant", "content": bot_response_content})

    return new_chat_history, new_chat_history, ""

with gr.Blocks(title="Aware NPC Chat") as demo:
    gr.Markdown("# Aware NPC Chat")
    knowledge_source = gr.Text(DEFAULT_FANDOM_URL, label="Knowledge source (Fandom Wiki URL) :")

    with gr.Row():
        with gr.Column():
            # Add the character selection dropdown
            character_dropdown = gr.Dropdown(
                label="You are chatting with",
                choices=character_names,
                value=default_character_name
            )
            displayed_image_component = gr.Image(
                type="pil",
                label="Your interlocutor",
                value=initial_pil_image_to_display
            )
        with gr.Column(variant='panel'):
            chatbot_display = gr.Chatbot(label="Chat", type="messages")

    chat_history_state = gr.State([])

    message_textbox = gr.Textbox(
        placeholder="Say something...",
        label="You're saying :"
    )

    submit_button = gr.Button("Send")

    # Update functions
    submit_button.click(
        fn=process_chat,
        inputs=[message_textbox, chat_history_state, character_dropdown],
        outputs=[chatbot_display, chat_history_state, message_textbox]
    )

    character_dropdown.change(
        fn=get_character_image,
        inputs=[character_dropdown, knowledge_source],
        outputs=[displayed_image_component]
    )

demo.launch()
