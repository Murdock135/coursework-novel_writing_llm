import os
from llm_config import get_llm
from load_env import load_env_vars
from config import Config
from novel_pipeline import run_novel_pipeline
from utilities.io import load_text

def main():
    # Load environment variables
    load_env_vars()
    
    # Initialize LLMs with Claude
    provider = "openrouter"
    model = "meta-llama/llama-4-maverick:free"
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
    
    # Modified pipeline run that will process just one act
    class LimitedPipelineRunner:
        def __init__(self, original_pipeline_func):
            self.original_func = original_pipeline_func
            
        def __call__(self, *args, **kwargs):
            # Get the original outline
            outline, stats = self.original_func(*args, **kwargs)
            
            # Limit to just the first act by modifying the outline
            if not kwargs.get('outline_only', False):
                print("Modifying pipeline: will only process the first act")
                # Save the first act, clear all others
                first_act = outline.acts[0]
                outline.acts = [first_act]
            
            return outline, stats
    
    # Replace run_novel_pipeline with our limited version
    limited_pipeline = LimitedPipelineRunner(run_novel_pipeline)
    
    # Run the modified novel writing pipeline
    outline, stats = limited_pipeline(
        story_path=story_path,
        novel_metadata=novel_metadata,
        outliner_llm=scene_llm,
        scene_writer_llm=scene_llm, 
        summarizer_llm=summary_llm,
        prompts=prompts,
        output_paths=output_paths,
        outline_only=False  # Set to True to only generate outline
    )

if __name__ == "__main__":
    main()