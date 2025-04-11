
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import Dict, Any
from output_schemas import NovelOutline

def create_outliner_prompt(prompt_text: str, novel_metadata: Dict[str, Any]):
    """Creates a prompt template for generating a novel outline."""
    # Create the prompt template with system and user messages directly
    return ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", "{user_input}")
    ]).partial(
        genre=novel_metadata.get('genre'),
        tone=novel_metadata.get('tone'),
        main_character=novel_metadata.get('main_character'),
        themes=novel_metadata.get('themes'),
        authors_message=novel_metadata.get('authors_message', None)
    )

def generate_novel_outline(llm, prompt_template, story_desc) -> NovelOutline:
    """Generates a novel outline using the LLM and parser."""
    parser = PydanticOutputParser(pydantic_object=NovelOutline)
    chain = prompt_template | llm | parser
    return chain.invoke({"user_input": story_desc})

