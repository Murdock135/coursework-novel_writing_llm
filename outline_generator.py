
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import Dict, Any, Tuple, Union, List, Optional
from output_schemas import NovelOutline
from utilities.io import load_text
from stats_tracker import StatsTracker

def generate_outline(
    llm: Any,
    prompt_path: str, 
    story_path: str,
    novel_metadata: Dict[str, Any] = None,
    stats_tracker: Optional[StatsTracker] = None
) -> NovelOutline:
    """Generate the novel outline using the specified prompt and story.
    
    Args:
        llm: The language model to use
        prompt_path: Path to the outliner prompt template
        story_path: Path to the story description
        novel_metadata: Optional metadata about the novel (genre, tone, etc.)
        stats_tracker: Optional stats tracker to count LLM calls
        
    Returns:
        The generated novel outline
    """
    # Load story description
    story_desc = load_text(story_path)
    
    # Load prompt text and create template
    outliner_prompt_raw_text = load_text(prompt_path)
    
    # Create prompt template
    outliner_prompt = ChatPromptTemplate.from_messages([
        ("system", outliner_prompt_raw_text),
        ("user", "{user_input}")
    ]).partial(
        genre=novel_metadata.get('genre', None),
        tone=novel_metadata.get('tone', None),
        main_character=novel_metadata.get('main_character', None),
        themes=novel_metadata.get('themes', None),
        authors_message=novel_metadata.get('authors_message', None)
    )
    
    # Generate novel outline as structured data
    parser = PydanticOutputParser(pydantic_object=NovelOutline)
    chain = outliner_prompt | llm | parser
    outline = chain.invoke({"user_input": story_desc})
    
    # Increment LLM call counter if stats tracker provided
    if stats_tracker:
        stats_tracker.increment_llm_calls()
    
    return outline

