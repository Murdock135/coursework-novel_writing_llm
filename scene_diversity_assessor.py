from typing import List
import random
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from utilities.io import load_text
from output_schemas import DiversityAssessment
from langchain_core.output_parsers import PydanticOutputParser

def assess_scene_diversity(
    llm: BaseChatModel,
    prompt_text: str,
    new_scene: str,
    existing_scenes: List[str],
    sample_size: int = 3,
    max_sample_length: int = 500,
    max_new_scene_length: int = 1000
) -> DiversityAssessment:
    """Assess if a newly generated scene is diverse enough compared to existing scenes.
    
    Args:
        llm: Language model to use for assessment
        prompt_text: The system prompt text for the assessor
        new_scene: The newly generated scene to assess
        existing_scenes: List of previously written scenes
        sample_size: Number of existing scenes to sample for comparison
        max_sample_length: Maximum characters to include from each sample scene
        max_new_scene_length: Maximum characters to include from new scene
        
    Returns:
        DiversityAssessment object with results and guidance
    """
    # If we don't have enough existing scenes for comparison, consider it diverse
    if len(existing_scenes) < 2:
        return DiversityAssessment(
            is_diverse_enough=True,
            analysis="Not enough existing scenes for comparison",
            guidance=None
        )
    
    # Sample a subset of existing scenes to avoid context window issues
    sample_size = min(sample_size, len(existing_scenes))
    sample_scenes = random.sample(existing_scenes, sample_size)
    
    # Truncate samples to manage context length
    truncated_samples = [scene[:max_sample_length] + "..." for scene in sample_scenes]
    truncated_new_scene = new_scene[:max_new_scene_length] + "..."
    
    # Create sample scenes text block
    separator = "=" * 30
    samples_text = ""
    for i, scene in enumerate(truncated_samples):
        samples_text += f"SAMPLE {i+1}:\n{scene}\n{separator}\n\n"
    
    # Create a parser for the output
    parser = PydanticOutputParser(pydantic_object=DiversityAssessment)
    
    # Build the assessment prompt
    assessment_prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_text.format(format_instructions=parser.get_format_instructions())),
        ("user", f"""Compare this new scene with existing samples for stylistic diversity:

EXISTING SCENES:
{separator}
{samples_text}

NEW SCENE:
{truncated_new_scene}""")
    ])
    
    # Execute assessment and parse the result
    assessment_chain = assessment_prompt | parser | llm
    return assessment_chain.invoke({})


def get_existing_scenes(scenes_dir: str, current_act: int, current_scene: int) -> List[str]:
    """Collect existing scenes up to the current scene for diversity comparison.
    
    Args:
        scenes_dir: Directory containing scene files
        current_act: Current act number
        current_scene: Current scene number within the act
        
    Returns:
        List of scene contents from previous scenes
    """
    existing_scenes = []
    
    # Iterate through all possible acts and scenes up to the current position
    for act_idx in range(1, current_act + 1):
        max_scene = current_scene if act_idx == current_act else 10
        for scene_idx in range(1, max_scene):
            scene_file = f"act{act_idx}_scene{scene_idx}.txt"
            scene_path = os.path.join(scenes_dir, scene_file)
            
            if os.path.exists(scene_path):
                try:
                    with open(scene_path, 'r') as f:
                        existing_scenes.append(f.read())
                except Exception as e:
                    print(f"Error reading {scene_path}: {e}")
    
    return existing_scenes