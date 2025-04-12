from typing import Dict, Any, Union, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel

def write_scene(llm: BaseChatModel, prompt_text: str, scene_description: str, novel_metadata: Dict[str, Union[str, List[str], None]]) -> str:
    """Generates a written scene using the LLM."""
    # Create the prompt template with system and user messages directly
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", "Write a scene based on this description: {scene_description}")
    ]).partial(
        genre=novel_metadata.get('genre'),
        tone=novel_metadata.get('tone'),
        main_character=novel_metadata.get('main_character'),
        themes=novel_metadata.get('themes'),
        authors_message=novel_metadata.get('authors_message', None)
    )
    
    # Execute the chain
    chain = prompt | llm
    return chain.invoke({"scene_description": scene_description}).content

def save_scene_to_file(scene_content: str, act_num: int, scene_num: int, output_dir: str) -> str:
    """Saves a scene to a file and returns the file path."""
    from utilities.io import save_content_to_file
    return save_content_to_file(scene_content, act_num, scene_num, output_dir, is_summary=False)