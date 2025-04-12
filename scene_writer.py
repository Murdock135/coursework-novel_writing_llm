from typing import Dict, Any, Union, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel

def write_scene(
    llm: BaseChatModel, 
    prompt_text: str, 
    scene_description: str, 
    novel_metadata: Dict[str, Union[str, List[str], None]], 
    relevant_context: Optional[str] = None
) -> str:
    """Generates a written scene using the LLM with optional context from relevant scenes."""
    # Modify user message based on whether we have relevant context
    if relevant_context:
        user_message = """Write a scene based on this description: {scene_description}
        
Use the following context from relevant scenes to maintain consistency and narrative flow:

{relevant_context}"""
    else:
        user_message = "Write a scene based on this description: {scene_description}"
    
    # Create the prompt template with system and user messages
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", user_message)
    ]).partial(
        genre=novel_metadata.get('genre'),
        tone=novel_metadata.get('tone'),
        main_character=novel_metadata.get('main_character'),
        themes=novel_metadata.get('themes'),
        authors_message=novel_metadata.get('authors_message', None)
    )
    
    # Execute the chain
    chain = prompt | llm
    return chain.invoke({
        "scene_description": scene_description,
        "relevant_context": relevant_context or ""
    }).content

