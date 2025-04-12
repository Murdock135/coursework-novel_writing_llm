import os
from llm_config import get_llm
from load_env import load_env_vars
from config import Config
from novel_pipeline import run_novel_pipeline
from utilities.io import load_text
from utilities.retrieval import SceneRetriever

def main():
    # Load environment variables
    load_env_vars()
    
    # Initialize LLMs with Ollama
    provider = "ollama"
    model = "gemma3:latest"
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
    
    # Prepare output paths dictionary
    output_paths = {
        'scenes': config.get_scenes_dir(),
        'summaries': config.get_summaries_dir()
    }
    
    # Initialize scene retriever
    scene_retriever = SceneRetriever(provider=provider)
    
    # Load any existing summaries if directory exists and has files
    summaries_dir = output_paths['summaries']
    if os.path.exists(summaries_dir):
        files = [f for f in os.listdir(summaries_dir) if f.startswith('summary_')]
        if files:
            print(f"Loading {len(files)} existing scene summaries for retrieval...")
            scene_retriever.load_summaries(summaries_dir)
        else:
            print("No existing summaries found to load.")
    else:
        print("Summaries directory does not exist yet.")
    
    # Custom function to generate one act only
    def run_one_act_pipeline(
        story_path, novel_metadata, outliner_llm, scene_writer_llm, 
        summarizer_llm, prompts, output_paths, outline_only=False, scene_retriever=None
    ):
        # Import needed modules
        from output_schemas import NovelOutline
        from outline_generator import generate_outline
        from stats_tracker import StatsTracker
        
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
        
        # Limit to just the first act
        if not outline_only:
            print("Limiting to first act only...")
            first_act = outline.acts[0]
            outline.acts = [first_act]
        
        # Exit if outline-only mode is specified
        if outline_only:
            print("Outline-only mode specified. Exiting without writing scenes.")
            return outline, stats_tracker
        
        # Start writing scenes for the first act only
        print("Starting to write scenes for the first act only...")
        
        # Get output directories
        scenes_dir = output_paths['scenes']
        summaries_dir = output_paths['summaries']
        
        # Ensure output directories exist
        import os
        os.makedirs(scenes_dir, exist_ok=True)
        os.makedirs(summaries_dir, exist_ok=True)
        
        # Loop through each scene in the first act
        for act_index, act in enumerate(outline.acts, 1):  # This will only process the first act
            for scene_index, scene in enumerate(act.scenes, 1):
                print(f"Writing Act {act_index}, Scene {scene_index}...")
                
                from novel_pipeline import process_scene
                error = process_scene(
                    act_index, scene_index, scene, scene_writer_llm, summarizer_llm,
                    prompts['scene'], prompts['summary'], scenes_dir, summaries_dir, 
                    stats_tracker, novel_metadata, scene_retriever
                )
        
        # Print statistics
        stats_tracker.print_statistics()
        print(f"\nFinished writing scenes for Act 1!")
        
        return outline, stats_tracker
    
    # Run our one-act pipeline instead of the full pipeline
    outline, stats = run_one_act_pipeline(
        story_path=story_path,
        novel_metadata=novel_metadata,
        outliner_llm=scene_llm,
        scene_writer_llm=scene_llm, 
        summarizer_llm=summary_llm,
        prompts=prompts,
        output_paths=output_paths,
        outline_only=False,  # Set to True to only generate outline
        scene_retriever=scene_retriever  # Add the scene retriever
    )

if __name__ == "__main__":
    main()