import os
from llm_config import get_llm
from load_env import load_env_vars
import argparse
from utilities.io import load_text
from config import Config
from plot_generator import create_outliner_prompt, generate_novel_outline
from typing import Dict, Any, List, Union
from output_schemas import NovelOutline

def parse_args():
    parser = argparse.ArgumentParser(
            prog='Novel Writer',
            description='Writes a novel using LLMs'
            )
    parser.add_argument('-p', '--provider', default='openrouter')
    parser.add_argument('-m', '--model', default="meta-llama/llama-4-maverick:free")
    return parser.parse_args()

if __name__ == "__main__":
    # load environment variables
    load_env_vars()

    # Get command line arguments and initialize LLM
    args = parse_args()
    llm = get_llm(args.provider, args.model)
  
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
    
    # Generate novel outline as structured data
    outline: NovelOutline = generate_novel_outline(llm, outliner_prompt, story_desc)
    
    # Print outline in a readable format
    print(outline.format_readable())

    # Start writing
    print("Starting writing now!!")

    
