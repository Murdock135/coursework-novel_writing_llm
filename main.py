import argparse
import os
from llm_config import get_llm
from load_env import load_env_vars
from config import Config
from novel_pipeline import run_novel_pipeline
from utilities.io import load_text, clear_directory
from utilities.retrieval import SceneRetriever

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

def load_prompts(config, diversity_assessor_enabled=True):
    """Load system prompts for the language models."""
    prompts = {
        'plot': config.plot_generator_prompt,
        'scene': load_text(config.scene_writer_prompt),
        'summary': load_text(config.scene_summary_generator_prompt)
    }
    
    # Add diversity assessor prompt if enabled
    if diversity_assessor_enabled:
        diversity_assessor_path = os.path.join(config.project_dir, "sys_messages/scene_diversity_assessor.txt")
        if os.path.exists(diversity_assessor_path):
            prompts['diversity_assessor'] = load_text(diversity_assessor_path)
    
    return prompts

def initialize_llms(args):
    """Initialize language models based on command line arguments."""
    # Main LLMs for scene writing and summarization
    scene_llm = get_llm(args.provider, args.model)
    summary_llm = get_llm(args.provider, args.summary_model)
    
    # Diversity assessor LLM (using same model as scene writer)
    diversity_assessor_llm = None
    if not args.no_diversity:
        diversity_assessor_llm = get_llm(args.provider, args.model)
    
    return scene_llm, summary_llm, diversity_assessor_llm

def initialize_retriever(args):
    """Initialize the scene retriever if enabled."""
    if args.no_retrieval:
        return None
    
    print("Initializing scene retriever for semantic search...")
    return SceneRetriever(provider=args.provider, model_name=args.embedding_model)

def prepare_output_directories(config, outline_only):
    """Prepare output directories and clear existing content if needed."""
    output_paths = {
        'scenes': config.get_scenes_dir(),
        'summaries': config.get_summaries_dir()
    }
    
    # Clear existing scenes and summaries if generating full novel
    if not outline_only:
        print("Clearing existing scenes and summaries...")
        clear_directory(output_paths['scenes'])
        clear_directory(output_paths['summaries'])
    
    return output_paths

if __name__ == "__main__":
    # Load environment variables
    load_env_vars()

    # Parse command line arguments
    args = parse_args()
    
    # Initialize config
    config = Config()
    
    # Initialize language models
    scene_llm, summary_llm, diversity_assessor_llm = initialize_llms(args)
    
    # Load system prompts
    prompts = load_prompts(config, diversity_assessor_enabled=not args.no_diversity)
    
    # Get novel metadata
    novel_metadata = config.get_novel_metadata()
    
    # Prepare story path and output directories
    story_path = os.path.join(config.project_dir, config.story_description)
    output_paths = prepare_output_directories(config, args.outline_only)
    
    # Initialize scene retriever if enabled
    scene_retriever = initialize_retriever(args)
    
    # Run the novel writing pipeline
    outline, stats = run_novel_pipeline(
        story_path=story_path,
        novel_metadata=novel_metadata,
        outliner_llm=scene_llm,  # Using same LLM for outline generation
        scene_writer_llm=scene_llm, 
        summarizer_llm=summary_llm,
        prompts=prompts,
        output_paths=output_paths,
        outline_only=args.outline_only,
        scene_retriever=scene_retriever,
        diversity_assessor_llm=diversity_assessor_llm
    )