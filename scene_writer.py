from typing import Dict, Any, Union, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
import os
from utilities.io import load_text

def create_scene_writing_prompt(prompt_text: str, novel_metadata: Dict[str, Union[str, List[str], None]]):
    """Creates a prompt template for writing a scene based on novel metadata."""
    return ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", "Write a scene based on this description: {scene_description}")
    ]).partial(
        genre=novel_metadata['genre'],
        tone=novel_metadata['tone'],
        main_character=novel_metadata['main_character'],
        themes=novel_metadata['themes']
    )

def write_scene(llm: BaseChatModel, prompt_template, scene_description: str) -> str:
    """Generates a written scene using the LLM."""
    chain = prompt_template | llm
    return chain.invoke({"scene_description": scene_description}).content

def save_scene_to_file(scene_content: str, act_num: int, scene_num: int, output_dir: str) -> str:
    """Saves a scene to a file and returns the file path."""
    os.makedirs(output_dir, exist_ok=True)
    
    file_name = f"act{act_num}_scene{scene_num}.txt"
    file_path = os.path.join(output_dir, file_name)
    
    with open(file_path, 'w') as f:
        f.write(scene_content)
    
    return file_path