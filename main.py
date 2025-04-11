import argparse
from llm_config import get_llm
from load_env import load_env_vars
from config import Config
from novel_pipeline import run_novel_pipeline

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
    
    # Run the novel writing pipeline
    outline, stats = run_novel_pipeline(scene_llm, summary_llm, config, args.outline_only)
