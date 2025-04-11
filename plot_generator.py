
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import Dict, Any
from output_schemas import NovelOutline

def create_outliner_prompt(prompt_text: str, novel_metadata: Dict[str, Any]):
    return ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", "{user_input}")]).partial(
        genre=novel_metadata['genre'],
        tone=novel_metadata['tone'],
        main_character=novel_metadata['main_character'],
        themes=novel_metadata['themes'],
        authors_message=novel_metadata['authors_message']
    )

def generate_novel_outline(llm, prompt_template, story_desc) -> NovelOutline:
    parser = PydanticOutputParser(pydantic_object=NovelOutline)
    chain = prompt_template | llm | parser
    return chain.invoke({"user_input": story_desc})

if __name__ == "__main__":
    pass
