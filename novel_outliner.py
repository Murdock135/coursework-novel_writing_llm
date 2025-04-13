import argparse
from typing import Dict, Any
from utilities.io import load_text
from llm_config import get_llm
from config import Config
from output_schemas import NovelOutline
from stats_tracker import StatsTracker
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from load_env import load_env_vars

def generate_outline(
    llm: Any,
    prompt_text: str, 
    novel_metadata: Dict[str, Any] = None,
    stats_tracker: StatsTracker = None
) -> NovelOutline:
    """Generate the novel outline using the specified prompt and story."""
    
    # Load story description
    try:
        story_desc = novel_metadata.get('story_description', None)
    except KeyError:
        raise ValueError("Story description not found in novel metadata.")
    
    # Load prompt text and create template
    outliner_prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", "{user_input}")
    ]).partial(
        genre=novel_metadata.get('genre', None),
        tone=novel_metadata.get('tone', None),
        main_character=novel_metadata.get('main_character_name', None),
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

if __name__ == "__main__":
    # Load environment variables
    load_env_vars()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate a novel outline using LLMs")
    parser.add_argument('-p', '--provider', default='openrouter', help='LLM provider to use')
    parser.add_argument('-m', '--model', default="meta-llama/llama-4-maverick:free", help='Model name to use')
    args = parser.parse_args()

    # Configure
    config = Config()
    novel_metadata = config.novel_metadata

    # Load prompts
    prompts = config.load_prompts()
    prompt_text = prompts['outliner_prompt']

    # Load language model
    outliner_llm = get_llm(args.provider, args.model)

    # Generate the outline
    print("Generating novel outline...")
    outline = generate_outline(
        llm = outliner_llm,
        prompt_text = prompt_text,
        novel_metadata = novel_metadata,
    )
    print("Outline generated successfully:")
    print(outline.format_readable())

