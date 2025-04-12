from typing import Dict, Any, Union, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel

def generate_scene_summary(llm: BaseChatModel, prompt_text: str, scene_content: str, novel_metadata: Dict[str, Union[str, List[str], None]]) -> str:
    """Generates a summary of a written scene using the LLM."""
    # Create the prompt template with system and user messages directly
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", "Create a concise summary of this written scene: {scene_content}")
    ]).partial(
        genre=novel_metadata.get('genre'),
        tone=novel_metadata.get('tone'),
        main_character=novel_metadata.get('main_character'),
        themes=novel_metadata.get('themes'),
        authors_message=novel_metadata.get('authors_message', None)
    )
    
    # Execute the chain
    chain = prompt | llm
    return chain.invoke({"scene_content": scene_content}).content

