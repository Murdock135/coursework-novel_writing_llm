
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import Dict, Any
from output_schemas import NovelOutline

from utilities.prompt_utils import create_prompt_template

def create_outliner_prompt(prompt_text: str, novel_metadata: Dict[str, Any]):
    return create_prompt_template(
        prompt_text=prompt_text,
        novel_metadata=novel_metadata,
        user_message="{var_placeholder}",
        var_name="user_input"
    )

def generate_novel_outline(llm, prompt_template, story_desc) -> NovelOutline:
    parser = PydanticOutputParser(pydantic_object=NovelOutline)
    chain = prompt_template | llm | parser
    return chain.invoke({"user_input": story_desc})

