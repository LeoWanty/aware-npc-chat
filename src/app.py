import gradio as gr
from PIL import Image  # Required for gr.Image(type="pil")


def process_chat(message, current_chat_history):
    """
    Processes a chat message by appending it to the current chat history and generating a
    simple echo response.

    Args:
    message (str): The user message to be processed.
    current_chat_history (list[dict[str, str]]): The existing chat history, where each entry
        contains a role ('user' or 'assistant') and its corresponding content.

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


with gr.Blocks(title="Chat with Image") as demo:
    gr.Markdown("## Chat with Image Uploader")

    with gr.Row():
        with gr.Column(scale=1):
            displayed_image_component = gr.Image(
                type="pil",
                label="Your interlocutor",
                value="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
                interactive=False
            )
        with gr.Column(scale=2):
            chatbot_display = gr.Chatbot(label="Chat", height=300, type="messages")

    chat_history_state = gr.State([])

    message_textbox = gr.Textbox(
        placeholder="Say something...",
        label="You're saying :"
    )

    submit_button = gr.Button("Send")

    submit_button.click(
        fn=process_chat,
        inputs=[message_textbox, chat_history_state],
        outputs=[chatbot_display, chat_history_state, message_textbox]
    )

demo.launch()
