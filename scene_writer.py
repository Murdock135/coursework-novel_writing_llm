from typing import Dict, Any, Union, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel

def write_scene(
    llm: BaseChatModel, 
    prompt_text: str, 
    scene_description: str, 
    novel_metadata: Dict[str, Union[str, List[str], None]], 
    relevant_context: Optional[str] = None,
    diversity_guidance: Optional[str] = None
) -> str:
    """Generates a written scene using the LLM with optional context from relevant scenes.
    
    Args:
        llm: Language model to use for generation
        prompt_text: System prompt text
        scene_description: Description of the scene to generate
        novel_metadata: Novel metadata (not used for prompt to improve diversity)
        relevant_context: Optional context from previous scenes
        diversity_guidance: Optional guidance from the diversity assessor
    """
    # Base user message with scene description
    user_message = "Write a scene based on this description: {scene_description}"
    
    # Add context from relevant scenes if available
    if relevant_context:
        user_message += """
        
Use the following context from relevant scenes as inspiration, but add your own creative direction:

{relevant_context}"""
    
    # Add diversity guidance if provided by assessor
    if diversity_guidance:
        user_message += f"""

DIVERSITY GUIDANCE:
{diversity_guidance}"""
    
    # Create the prompt template with system and user messages
    # Remove novel_metadata to avoid consistent style/tone
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text),
        ("user", user_message)
    ])
    
    # Execute the chain
    chain = prompt | llm
    return chain.invoke({
        "scene_description": scene_description,
        "relevant_context": relevant_context or ""
    }).content