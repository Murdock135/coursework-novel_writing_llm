import argparse
import os
import subprocess
from llm_config import get_llm
from load_env import load_env_vars
from config import Config
from novel_pipeline import run_novel_pipeline
from utilities.io import clear_directory
from stats_tracker import StatsTracker

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
    parser.add_argument('--no-stats', action='store_true', help='Disable statistics tracking')
    return parser.parse_args()


def initialize_llms(args):
    """Initialize language models based on command line arguments."""
    outliner_llm = get_llm(args.provider, args.model)
    scene_llm = get_llm(args.provider, args.model)
    summary_llm = get_llm(args.provider, args.summary_model)
    diversity_assessor_llm = get_llm(args.provider, args.model) if not args.no_diversity else None
    
    return outliner_llm, scene_llm, summary_llm, diversity_assessor_llm

if __name__ == "__main__":
    # Load environment variables
    load_env_vars()

    # Parse command line arguments
    args = parse_args()
    
    # Initialize stats tracker
    stats_tracker = None if args.no_stats else StatsTracker()
    
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
    output_paths_dict = config.get_output_paths()
    prompts_dict = config.load_prompts()

    # Initialize language models
    outliner_llm, scene_llm, summary_llm, diversity_assessor_llm = initialize_llms(args)

    run_novel_pipeline(
        config.novel_metadata,
        outliner_llm,
        scene_llm,
        summary_llm,
        diversity_assessor_llm,
        prompts_dict,
        output_paths_dict,
        max_retries=3,
        stats_tracker=stats_tracker,
    )
    
    # Print statistics if tracking is enabled
    if stats_tracker:
        stats_tracker.print_statistics()

