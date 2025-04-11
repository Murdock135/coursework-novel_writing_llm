import os
import time
from typing import Dict, List, Union, Tuple, Optional, Any
from output_schemas import NovelOutline
from utilities.io import load_text, get_scene_path
from plot_generator import create_outliner_prompt, generate_novel_outline
from scene_writer import create_scene_writing_prompt, write_scene, save_scene_to_file
from scene_summary_generator import create_summary_generation_prompt, generate_scene_summary, save_summary_to_file
from stats_tracker import StatsTracker
from config import Config

def generate_outline(
    llm: Any, 
    config: Config, 
    stats_tracker: StatsTracker
) -> Tuple[NovelOutline, Dict[str, Union[str, List[str], None]]]:
    """Generate the novel outline and return it along with the novel metadata."""
    novel_metadata = config.get_novel_metadata()
    
    # Get story description from config
    story_desc_path = os.path.join(config.project_dir, config.story_description)
    story_desc = load_text(story_desc_path)
    
    # Create prompt template
    outliner_prompt_raw_text = load_text(config.plot_generator_prompt)
    outliner_prompt = create_outliner_prompt(outliner_prompt_raw_text, novel_metadata)
    
    # Generate novel outline as structured data
    outline = generate_novel_outline(llm, outliner_prompt, story_desc)
    
    # Increment LLM call counter
    stats_tracker.increment_llm_calls()
    
    return outline, novel_metadata



def process_scene(
    act_index: int, 
    scene_index: int, 
    scene: Any,
    scene_llm: Any, 
    summary_llm: Any, 
    scene_prompt: str, 
    summary_prompt: str,
    scenes_dir: str, 
    summaries_dir: str, 
    stats_tracker: StatsTracker
) -> Optional[str]:
    """Process a single scene: generate content and summary.
    
    Returns:
        An error message if an error occurred, None otherwise.
    """
    # Create file paths
    scene_file_path = get_scene_path(act_index, scene_index, scenes_dir, is_summary=False)
    summary_file_path = get_scene_path(act_index, scene_index, summaries_dir, is_summary=True)
    
    try:
        # Generate scene content (always overwrite existing files)
        print(f"Generating scene content for Act {act_index}, Scene {scene_index}...")
        scene_content = write_scene(scene_llm, scene_prompt, scene.description)
        stats_tracker.increment_llm_calls()
        stats_tracker.increment_scenes()
        
        # Save scene to file
        save_scene_to_file(scene_content, act_index, scene_index, scenes_dir)
        print(f"Saved scene to {scene_file_path}")
        print(f"LLM calls so far: {stats_tracker.llm_call_count}")
        
        # Generate summary (always overwrite existing files)
        print(f"Generating summary for Act {act_index}, Scene {scene_index}...")
        scene_summary = generate_scene_summary(summary_llm, summary_prompt, scene_content)
        stats_tracker.increment_llm_calls()
        stats_tracker.increment_summaries()
        
        # Save summary to file
        save_summary_to_file(scene_summary, act_index, scene_index, summaries_dir)
        print(f"Saved summary to {summary_file_path}")
        print(f"LLM calls so far: {stats_tracker.llm_call_count}")
        
        # Add a small delay to avoid rate limiting
        time.sleep(2)
        
        return None
    
    except Exception as e:
        error_msg = f"Error processing Act {act_index}, Scene {scene_index}: {str(e)}"
        stats_tracker.add_error(error_msg)
        return error_msg

def run_novel_pipeline(
    scene_llm: Any, 
    summary_llm: Any, 
    config: Config,
    scene_prompt,
    summary_prompt,
    outline_only: bool = False
) -> Tuple[NovelOutline, StatsTracker]:
    """Run the complete novel writing pipeline."""
    # Initialize stats tracker
    stats_tracker = StatsTracker()
    
    # Generate outline
    outline, novel_metadata = generate_outline(scene_llm, config, stats_tracker)
    
    # Print outline in a readable format
    print(outline.format_readable())
    print(f"LLM calls so far: {stats_tracker.llm_call_count}")

    # Exit if outline-only mode is specified
    if outline_only:
        print("Outline-only mode specified. Exiting without writing scenes.")
        return outline, stats_tracker

    # Start writing individual scenes
    print("Starting to write individual scenes...")
    
    # Get output directories from config
    scenes_dir = config.get_scenes_dir()
    summaries_dir = config.get_summaries_dir()
    
    # Loop through each act and scene to write content
    scene_count = 0
    
    for act_index, act in enumerate(outline.acts, 1):
        for scene_index, scene in enumerate(act.scenes, 1):
            scene_count += 1
            print(f"Writing Act {act_index}, Scene {scene_index} ({scene_count} of {sum(len(act.scenes) for act in outline.acts)})...")
            
            error = process_scene(
                act_index, scene_index, scene, scene_llm, summary_llm,
                scene_prompt, summary_prompt, scenes_dir, summaries_dir, stats_tracker
            )
    
    # Print statistics
    stats_tracker.print_statistics()
    
    print(f"\nFinished writing all {scene_count} scenes and summaries!")
    print(f"Scene files are stored in: {scenes_dir}")
    print(f"Summary files are stored in: {summaries_dir}")
    
    return outline, stats_tracker