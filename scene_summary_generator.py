from typing import Dict, Any, Union, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
import os
from utilities.io import load_text

def create_summary_generation_prompt(prompt_text: str, novel_metadata: Dict[str, Union[str, List[str], None]]):
    """Creates a prompt template for summarizing written scenes based on novel metadata."""
    return ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", "Create a concise summary of this written scene: {scene_content}")
    ]).partial(
        genre=novel_metadata['genre'],
        tone=novel_metadata['tone'],
        main_character=novel_metadata['main_character'],
        themes=novel_metadata['themes']
    )

def generate_scene_summary(llm: BaseChatModel, prompt_template, scene_content: str) -> str:
    """Generates a summary of a written scene using the LLM."""
    chain = prompt_template | llm
    return chain.invoke({"scene_content": scene_content}).content

def save_summary_to_file(summary_content: str, act_num: int, scene_num: int, output_dir: str) -> str:
    """Saves a scene summary to a file and returns the file path."""
    os.makedirs(output_dir, exist_ok=True)
    
    file_name = f"act{act_num}_scene{scene_num}.txt"
    file_path = os.path.join(output_dir, file_name)
    
    with open(file_path, 'w') as f:
        f.write(summary_content)
    
    return file_path