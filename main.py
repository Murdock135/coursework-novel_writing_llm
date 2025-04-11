import os
from llm_config import get_llm
from load_env import load_env_vars
import argparse
from utilities.io import load_text
from config import Config
from plot_generator import create_outliner_prompt, generate_novel_outline
from scene_writer import create_scene_writing_prompt, write_scene, save_scene_to_file
from scene_summary_generator import create_summary_generation_prompt, generate_scene_summary, save_summary_to_file
from typing import Dict, Any, List, Union
from output_schemas import NovelOutline
import time

def parse_args():
    parser = argparse.ArgumentParser(
            prog='Novel Writer',
            description='Writes a novel using LLMs'
            )
    parser.add_argument('-p', '--provider', default='openrouter')
    parser.add_argument('-m', '--model', default="meta-llama/llama-4-maverick:free")
    parser.add_argument('-s', '--summary-model', default="meta-llama/llama-4-maverick:free", help='Model to use for scene summarization')
    parser.add_argument('-o', '--outline-only', action='store_true', help='Generate only the outline without writing scenes')
    return parser.parse_args()

if __name__ == "__main__":
    # load environment variables
    load_env_vars()

    # Get command line arguments and initialize LLMs
    args = parse_args()
    scene_llm = get_llm(args.provider, args.model)
    summary_llm = get_llm(args.provider, args.summary_model)
  
    # Novel metadata (genre, tone, etc)
    config = Config()
    novel_metadata: Dict[str, Union[str, List[str], None]] = config.get_novel_metadata()
    
    # Get story description
    story_desc_path = os.path.join(config.project_dir, 'data', 'story.txt')
    with open(story_desc_path, 'r') as f:
        story_desc = f.read()
    
    # Create prompt template
    outliner_prompt_raw_text = load_text(config.plot_generator_prompt)
    outliner_prompt = create_outliner_prompt(outliner_prompt_raw_text, novel_metadata)
    
    # Track LLM calls
    llm_call_count = 1  # Start at 1 for the outline generation
    
    # Generate novel outline as structured data
    outline: NovelOutline = generate_novel_outline(scene_llm, outliner_prompt, story_desc)
    
    # Print outline in a readable format
    print(outline.format_readable())
    print(f"LLM calls so far: {llm_call_count}")

    # Exit if outline-only mode is specified
    if args.outline_only:
        print("Outline-only mode specified. Exiting without writing scenes.")
        exit(0)

    # Start writing individual scenes
    print("Starting to write individual scenes...")
    
    # Create scene writing prompt
    scene_prompt_path = os.path.join(config.path_to_prompts, 'scene_writer.txt')
    scene_prompt_raw_text = load_text(scene_prompt_path)
    scene_prompt = create_scene_writing_prompt(scene_prompt_raw_text, novel_metadata)
    
    # Create summary generation prompt
    summary_prompt_path = os.path.join(config.path_to_prompts, 'scene_summary_generator.txt')
    summary_prompt_raw_text = load_text(summary_prompt_path)
    summary_prompt = create_summary_generation_prompt(summary_prompt_raw_text, novel_metadata)
    
    # Create directories if they don't exist
    scenes_dir = os.path.join(config.project_dir, config.scenes_path)
    os.makedirs(scenes_dir, exist_ok=True)
    
    summaries_dir = os.path.join(config.project_dir, config.scene_summaries_path)
    os.makedirs(summaries_dir, exist_ok=True)
    
    # Loop through each act and scene to write content
    scene_count = 0
    for act_index, act in enumerate(outline.acts, 1):
        for scene_index, scene in enumerate(act.scenes, 1):
            scene_count += 1
            print(f"Writing Act {act_index}, Scene {scene_index} ({scene_count} of {sum(len(act.scenes) for act in outline.acts)})...")
            
            # Create file paths
            scene_file_name = f"act{act_index}_scene{scene_index}.txt"
            scene_file_path = os.path.join(scenes_dir, scene_file_name)
            
            summary_file_name = f"act{act_index}_scene{scene_index}.txt"
            summary_file_path = os.path.join(summaries_dir, summary_file_name)
            
            if os.path.exists(scene_file_path) and os.path.exists(summary_file_path):
                print(f"Scene and summary files for Act {act_index}, Scene {scene_index} already exist. Skipping generation.")
                continue
            
            try:
                # Generate scene content if it doesn't exist
                if not os.path.exists(scene_file_path):
                    scene_content = write_scene(scene_llm, scene_prompt, scene.description)
                    llm_call_count += 1
                    
                    # Save scene to file
                    save_scene_to_file(scene_content, act_index, scene_index, scenes_dir)
                    print(f"Saved scene to {scene_file_path}")
                    print(f"LLM calls so far: {llm_call_count}")
                else:
                    # Read existing scene content
                    with open(scene_file_path, 'r') as f:
                        scene_content = f.read()
                    print(f"Using existing scene from {scene_file_path}")
                
                # Generate summary if it doesn't exist
                if not os.path.exists(summary_file_path):
                    scene_summary = generate_scene_summary(summary_llm, summary_prompt, scene_content)
                    llm_call_count += 1
                    
                    # Save summary to file
                    save_summary_to_file(scene_summary, act_index, scene_index, summaries_dir)
                    print(f"Saved summary to {summary_file_path}")
                    print(f"LLM calls so far: {llm_call_count}")
                
                # Add a small delay to avoid rate limiting
                time.sleep(2)
            
            except Exception as e:
                print(f"Error processing Act {act_index}, Scene {scene_index}: {str(e)}")
    
    print(f"Finished writing all {scene_count} scenes and summaries!")
    print(f"Total LLM calls: {llm_call_count}")
    print(f"Scene files are stored in: {scenes_dir}")
    print(f"Summary files are stored in: {summaries_dir}")
