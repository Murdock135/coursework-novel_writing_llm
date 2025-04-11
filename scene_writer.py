from typing import Dict, Any, Union, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel

from utilities.prompt_utils import create_prompt_template

def create_scene_writing_prompt(prompt_text: str, novel_metadata: Dict[str, Union[str, List[str], None]]):
    """Creates a prompt template for writing a scene based on novel metadata."""
    return create_prompt_template(
        prompt_text=prompt_text,
        novel_metadata=novel_metadata,
        user_message="Write a scene based on this description: {var_placeholder}",
        var_name="scene_description"
    )

def write_scene(llm: BaseChatModel, prompt_template, scene_description: str) -> str:
    """Generates a written scene using the LLM."""
    chain = prompt_template | llm
    return chain.invoke({"scene_description": scene_description}).content

def save_scene_to_file(scene_content: str, act_num: int, scene_num: int, output_dir: str) -> str:
    """Saves a scene to a file and returns the file path."""
    from utilities.io import save_content_to_file
    return save_content_to_file(scene_content, act_num, scene_num, output_dir, is_summary=False)