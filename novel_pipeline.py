import os
import time
from typing import Dict, List, Union, Tuple, Optional, Any
from output_schemas import NovelOutline
from utilities.io import get_scene_path, load_text, pretty_print_scene
from outline_generator import generate_outline
from scene_writer import write_scene
from scene_summary_generator import generate_scene_summary
from stats_tracker import StatsTracker

def process_scene(
    act_index: int, 
    scene_index: int, 
    scene: Any,
    scene_llm: Any, 
    summary_llm: Any, 
    scene_prompt_text: str, 
    summary_prompt_text: str,
    scenes_dir: str, 
    summaries_dir: str, 
    stats_tracker: StatsTracker,
    novel_metadata: Dict[str, Any],
    scene_retriever: Optional[Any] = None
) -> Optional[str]:
    """Process a single scene: generate content and summary.
    
    Returns:
        An error message if an error occurred, None otherwise.
    """
    # Create file paths
    scene_file_path = get_scene_path(act_index, scene_index, scenes_dir, is_summary=False)
    summary_file_path = get_scene_path(act_index, scene_index, summaries_dir, is_summary=True)
    
    try:
        # Get relevant context from previous scenes if retriever is available
        relevant_context = None
        if scene_retriever is not None:
            print(f"Retrieving relevant context for Act {act_index}, Scene {scene_index}...")
            relevant_context = scene_retriever.get_relevant_context(scene.description)
            if relevant_context:
                print(f"Found relevant context from {relevant_context.count('Previous Scene')} scene(s)")
        
        # Generate scene content (always overwrite existing files)
        print(f"Generating scene content for Act {act_index}, Scene {scene_index}...")
        scene_content = write_scene(
            scene_llm, 
            scene_prompt_text, 
            scene.description, 
            novel_metadata,
            relevant_context
        )
        stats_tracker.increment_llm_calls()
        stats_tracker.increment_scenes()
        
        # Save scene to file
        with open(scene_file_path, 'w') as f:
            f.write(scene_content)
        print(f"Saved scene to {scene_file_path}")
        
        # Pretty print the scene
        pretty_print_scene(act_index, scene_index, scene_content)
        
        print(f"LLM calls so far: {stats_tracker.llm_call_count}")
        
        # Generate summary (always overwrite existing files)
        print(f"Generating summary for Act {act_index}, Scene {scene_index}...")
        scene_summary = generate_scene_summary(summary_llm, summary_prompt_text, scene_content, novel_metadata)
        stats_tracker.increment_llm_calls()
        stats_tracker.increment_summaries()
        
        # Save summary to file
        with open(summary_file_path, 'w') as f:
            f.write(scene_summary)
        print(f"Saved summary to {summary_file_path}")
        print(f"LLM calls so far: {stats_tracker.llm_call_count}")
        
        # Update the retriever with the new summary if available
        if scene_retriever is not None:
            scene_retriever.load_summaries(summaries_dir)
        
        # Add a small delay to avoid rate limiting
        time.sleep(2)
        
        return None
    
    except Exception as e:
        error_msg = f"Error processing Act {act_index}, Scene {scene_index}: {str(e)}"
        stats_tracker.add_error(error_msg)
        return error_msg

def run_novel_pipeline(
    story_path: str,
    novel_metadata: Dict[str, Any],
    outliner_llm: Any,
    scene_writer_llm: Any,
    summarizer_llm: Any,
    prompts: Dict[str, str],
    output_paths: Dict[str, str],
    outline_only: bool = False,
    scene_retriever: Optional[Any] = None
) -> Tuple[NovelOutline, StatsTracker]:
    """Run the complete novel writing pipeline."""
    # Initialize stats tracker
    stats_tracker = StatsTracker()
    
    # Generate outline
    outline = generate_outline(
        outliner_llm, 
        prompts['plot'], 
        story_path,
        novel_metadata,
        stats_tracker
    )
    
    # Print outline in a readable format
    print(outline.format_readable())
    print(f"LLM calls so far: {stats_tracker.llm_call_count}")

    # Exit if outline-only mode is specified
    if outline_only:
        print("Outline-only mode specified. Exiting without writing scenes.")
        return outline, stats_tracker

    # Start writing individual scenes
    print("Starting to write individual scenes...")
    
    # Get output directories
    scenes_dir = output_paths['scenes']
    summaries_dir = output_paths['summaries']
    
    # Ensure output directories exist
    os.makedirs(scenes_dir, exist_ok=True)
    os.makedirs(summaries_dir, exist_ok=True)
    
    # Loop through each act and scene to write content
    scene_count = 0
    
    for act_index, act in enumerate(outline.acts, 1):
        for scene_index, scene in enumerate(act.scenes, 1):
            scene_count += 1
            print(f"Writing Act {act_index}, Scene {scene_index} ({scene_count} of {sum(len(act.scenes) for act in outline.acts)})...")
            
            error = process_scene(
                act_index, scene_index, scene, scene_writer_llm, summarizer_llm,
                prompts['scene'], prompts['summary'], scenes_dir, summaries_dir, 
                stats_tracker, novel_metadata, scene_retriever
            )
    
    # Print statistics
    stats_tracker.print_statistics()
    
    print(f"\nFinished writing all {scene_count} scenes and summaries!")
    print(f"Scene files are stored in: {scenes_dir}")
    print(f"Summary files are stored in: {summaries_dir}")
    
    return outline, stats_tracker
