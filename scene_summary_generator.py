from typing import Dict, Any, Union, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel

def create_summary_generation_prompt(prompt_text: str, novel_metadata: Dict[str, Union[str, List[str], None]]):
    """Creates a prompt template for summarizing written scenes based on novel metadata."""
    # Create the prompt template with system and user messages directly
    return ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", "Create a concise summary of this written scene: {scene_content}")
    ]).partial(
        genre=novel_metadata.get('genre'),
        tone=novel_metadata.get('tone'),
        main_character=novel_metadata.get('main_character'),
        themes=novel_metadata.get('themes'),
        authors_message=novel_metadata.get('authors_message', None)
    )

def generate_scene_summary(llm: BaseChatModel, prompt_template, scene_content: str) -> str:
    """Generates a summary of a written scene using the LLM."""
    chain = prompt_template | llm
    return chain.invoke({"scene_content": scene_content}).content

def save_summary_to_file(summary_content: str, act_num: int, scene_num: int, output_dir: str) -> str:
    """Saves a scene summary to a file and returns the file path."""
    from utilities.io import save_content_to_file
    return save_content_to_file(summary_content, act_num, scene_num, output_dir, is_summary=True)