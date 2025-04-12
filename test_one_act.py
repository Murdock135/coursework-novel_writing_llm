import os
import argparse
from llm_config import get_llm
from load_env import load_env_vars
from config import Config
from novel_pipeline import process_scene
from utilities.io import load_text, clear_directory
from utilities.retrieval import SceneRetriever
from output_schemas import NovelOutline
from outline_generator import generate_outline
from stats_tracker import StatsTracker

def run_test_pipeline(
    story_path, novel_metadata, outliner_llm, scene_writer_llm, 
    summarizer_llm, prompts, output_paths, num_acts=1, outline_only=False, scene_retriever=None
):
    # Initialize stats tracker
    stats_tracker = StatsTracker()
    
    # Generate the complete outline first
    print("Generating complete outline...")
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
    
    # Limit to specified number of acts
    if not outline_only and num_acts < len(outline.acts):
        print(f"Limiting to first {num_acts} act(s) only...")
        outline.acts = outline.acts[:num_acts]
    
    # Exit if outline-only mode is specified
    if outline_only:
        print("Outline-only mode specified. Exiting without writing scenes.")
        return outline, stats_tracker
    
    # Start writing scenes for the specified acts
    print(f"Starting to write scenes for the first {num_acts} act(s)...")
    
    # Get output directories
    scenes_dir = output_paths['scenes']
    summaries_dir = output_paths['summaries']
    
    # Ensure output directories exist
    os.makedirs(scenes_dir, exist_ok=True)
    os.makedirs(summaries_dir, exist_ok=True)
    
    # Loop through each scene in the specified acts
    for act_index, act in enumerate(outline.acts, 1):
        for scene_index, scene in enumerate(act.scenes, 1):
            print(f"Writing Act {act_index}, Scene {scene_index}...")
            
            error = process_scene(
                act_index, scene_index, scene, scene_writer_llm, summarizer_llm,
                prompts['scene'], prompts['summary'], scenes_dir, summaries_dir, 
                stats_tracker, novel_metadata, scene_retriever
            )
            
            # After each scene is processed and its summary generated,
            # update the scene retriever with the new summaries
            if scene_retriever is not None:
                scene_retriever.load_summaries(summaries_dir)
    
    # Print statistics
    stats_tracker.print_statistics()
    print(f"\nFinished writing scenes for {num_acts} act(s)!")
    
    return outline, stats_tracker

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test the novel generation pipeline')
    parser.add_argument('-a', '--acts', type=int, default=1, 
                        help='Number of acts to generate (default: 1)')
    parser.add_argument('-o', '--outline-only', action='store_true',
                        help='Generate only the outline without writing scenes')
    parser.add_argument('-p', '--provider', type=str, default='ollama',
                        help='LLM provider to use (default: ollama)')
    parser.add_argument('-m', '--model', type=str, default='gemma3:latest',
                        help='Model name to use (default: gemma3:latest)')
    parser.add_argument('-e', '--embedding-model', type=str, default='llama3.2:latest',
                        help='Model to use for embeddings in scene retrieval (default: llama3.2:latest)')
    parser.add_argument('-r', '--no-retrieval', action='store_true',
                        help='Disable scene retrieval for context')
    args = parser.parse_args()
    
    # Load environment variables
    load_env_vars()
    
    # Initialize LLMs with specified provider and model
    provider = args.provider
    model = args.model
    scene_llm = get_llm(provider, model)
    summary_llm = get_llm(provider, model)
    
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
    
    # Prepare output paths dictionary using test directories
    test_scenes_dir = os.path.join(config.project_dir, config.test_scenes_path)
    test_summaries_dir = os.path.join(config.project_dir, config.test_summaries_path)
    
    # Ensure test directories exist
    os.makedirs(test_scenes_dir, exist_ok=True)
    os.makedirs(test_summaries_dir, exist_ok=True)
    
    output_paths = {
        'scenes': test_scenes_dir,
        'summaries': test_summaries_dir
    }
    
    # Clear existing scenes and summaries
    print("Clearing existing scenes and summaries...")
    clear_directory(output_paths['scenes'])
    clear_directory(output_paths['summaries'])
    
    # Initialize scene retriever with specified embedding model
    scene_retriever = None
    if not args.no_retrieval:
        print("Initializing scene retriever for context-aware scene generation...")
        scene_retriever = SceneRetriever(provider=provider, model_name=args.embedding_model)
    
    # Run our test pipeline
    outline, stats = run_test_pipeline(
        story_path=story_path,
        novel_metadata=novel_metadata,
        outliner_llm=scene_llm,
        scene_writer_llm=scene_llm, 
        summarizer_llm=summary_llm,
        prompts=prompts,
        output_paths=output_paths,
        num_acts=args.acts,
        outline_only=args.outline_only,
        scene_retriever=scene_retriever
    )

if __name__ == "__main__":
    main()