import argparse
import os
import subprocess
from llm_config import get_llm
from load_env import load_env_vars
from config import Config
from novel_pipeline import run_novel_pipeline
from utilities.io import clear_directory

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
            prog='Novel Writer',
            description='Writes a novel using LLMs'
            )
    parser.add_argument('-p', '--provider', default='openrouter')
    parser.add_argument('-m', '--model', default="meta-llama/llama-4-maverick:free")
    parser.add_argument('-s', '--summary-model', default="meta-llama/llama-4-maverick:free", help='Model to use for scene summarization')
    parser.add_argument('-o', '--outline-only', action='store_true', help='Generate only the outline without writing scenes')
    parser.add_argument('-r', '--no-retrieval', action='store_true', help='Disable semantic retrieval of previous scene context')
    parser.add_argument('-e', '--embedding-model', default=None, help='Model to use for embeddings (if using retrieval)')
    parser.add_argument('--no-diversity', action='store_true', help='Disable scene diversity assessment')
    return parser.parse_args()

def get_prompts_paths(config, diversity_assessor_enabled=True):
    """Get paths to system prompts for the language models."""
    prompts = {
        'plot': config.plot_generator_prompt,
        'scene': config.scene_writer_prompt,
        'summary': config.scene_summary_generator_prompt,
        'assessor': config.diversity_assessor_prompt if diversity_assessor_enabled else None
    }
    return prompts

def initialize_llms(args):
    """Initialize language models based on command line arguments."""
    outliner_llm = get_llm(args.provider, args.model)
    scene_llm = get_llm(args.provider, args.model)
    summary_llm = get_llm(args.provider, args.summary_model)
    diversity_assessor_llm = get_llm(args.provider, args.model) if not args.no_diversity else None
    
    return outliner_llm, scene_llm, summary_llm, diversity_assessor_llm

def prepare_output_directories(config):
    """Prepare output directories and clear existing content if needed."""
    output_paths = {
        'plot_outline': config.plot_outline_path,
        'scenes': config.scenes_path,
        'scene_summaries': config.scene_summaries_path,
        'diversity_assessment': config.diversity_assessment_path,
    }

    # Clear existing scenes and summaries 
    print("Clearing existing scenes and summaries...")
    clear_directory(output_paths['scenes'])
    clear_directory(output_paths['scene_summaries'])
    
    return output_paths

if __name__ == "__main__":
    # Load environment variables
    load_env_vars()

    # Parse command line arguments
    args = parse_args()
    
    # If outline only, simply run novel outliner
    if args.outline_only:
        print("Outline-only mode specified. Running novel_outliner.py...")
        subprocess.run([
            "python3", 
            "novel_outliner.py", 
            "-p", args.provider, 
            "-m", args.model
        ])
        exit(0)
    
    # Initialize config
    config = Config()

    # Initialize language models
    outliner_llm, scene_llm, summary_llm, diversity_assessor_llm = initialize_llms(args)
    
    # Load system prompt paths
    prompt_paths = get_prompts_paths(config, diversity_assessor_enabled=not args.no_diversity)
    
    # Get novel metadata
    novel_metadata = config.get_novel_metadata()
    
    # Prepare story path and output directories
    story_path = config.story_description_path
    output_paths = prepare_output_directories(config)
    
    # Run the novel pipeline
    run_novel_pipeline(
        story_description_path=story_path,
        novel_metadata=novel_metadata,
        outliner_llm=scene_llm,
        scene_writer_llm=scene_llm,
        summarizer_llm=summary_llm,
        diversity_assessor_llm=diversity_assessor_llm,
        prompt_paths_dict=prompt_paths, 
        output_paths_dict=output_paths
    )

