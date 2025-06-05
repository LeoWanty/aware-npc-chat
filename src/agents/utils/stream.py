def stream_agent_output(agent_output_stream, keyword = "Answer:", end_keyword:str | None = None):
    """
    Buffers the agent output stream until "Answer:" is encountered,
    then starts yielding the stream text.

    Parameters:
        agent_output_stream: An iterable stream of text from the AI agent.
        keyword: The keyword indicating the start of the agent's output.
        end_keyword: The keyword indicating the end of the agent's output.
    Yields:
        str: Chunks of the agent's output stream after "Answer:" is encountered.
    """
    buffer = ""

    for chunk in agent_output_stream:
        buffer += chunk

        # Check if the keyword is in the buffer
        if keyword in buffer:
            # Find the position of the keyword
            keyword_index = buffer.index(keyword)

            # Yield the part of the buffer after the keyword
            output_after_keyword = buffer[keyword_index + len(keyword):]
            if output_after_keyword:
                yield output_after_keyword

            # Keep the remaining part of the buffer that hasn't been yielded yet
            buffer = buffer[keyword_index + len(keyword):]
        else:
            # If the keyword is not found, continue buffering
            continue
