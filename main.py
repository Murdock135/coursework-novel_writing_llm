import argparse
import os
from llm_config import get_llm
from load_env import load_env_vars
from config import Config
from novel_pipeline import run_novel_pipeline
from utilities.io import load_text

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
    # Load environment variables
    load_env_vars()

    # Get command line arguments
    args = parse_args()
    
    # Initialize LLMs
    scene_llm = get_llm(args.provider, args.model)
    summary_llm = get_llm(args.provider, args.summary_model)
    
    # Initialize config
    config = Config()
    
    # Get novel metadata
    novel_metadata = config.get_novel_metadata()
    
    # Load prompt text
    scene_prompt_text = load_text(config.scene_writer_prompt)
    summary_prompt_text = load_text(config.scene_summary_generator_prompt)
    
    # Prepare the story path
    story_path = os.path.join(config.project_dir, config.story_description)
    
    # Prepare prompts dictionary
    prompts = {
        'plot': config.plot_generator_prompt,
        'scene': scene_prompt_text,
        'summary': summary_prompt_text
    }
    
    # Prepare output paths dictionary
    output_paths = {
        'scenes': config.get_scenes_dir(),
        'summaries': config.get_summaries_dir()
    }
    
    # Run the novel writing pipeline
    outline, stats = run_novel_pipeline(
        story_path,
        novel_metadata,
        scene_llm,  # Using same LLM for outline generation
        scene_llm, 
        summary_llm,
        prompts,
        output_paths,
        args.outline_only
    )
