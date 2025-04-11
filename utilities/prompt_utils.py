from typing import Dict, Any, Union, List
from langchain_core.prompts import ChatPromptTemplate

def create_prompt_template(prompt_text: str, novel_metadata: Dict[str, Any], user_message: str, var_name: str):
    """
    Creates a standardized prompt template for various LLM tasks.
    
    Args:
        prompt_text: The system prompt text
        novel_metadata: Novel metadata dictionary
        user_message: Template for the user message with a placeholder
        var_name: The variable name to be used in the placeholder
        
    Returns:
        Configured ChatPromptTemplate
    """
    # Build the user message with the appropriate variable placeholder
    user_template = user_message.format(var_placeholder=f"{{{var_name}}}")
    
    # Create the prompt template with system and user messages
    return ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", user_template)
    ]).partial(
        genre=novel_metadata.get('genre'),
        tone=novel_metadata.get('tone'),
        main_character=novel_metadata.get('main_character'),
        themes=novel_metadata.get('themes'),
        authors_message=novel_metadata.get('authors_message', None)
    )