import os
import json
from typing import Dict, Any
import sys
sys.path.append('..')
from novel_pipeline import run_novel_pipeline, process_scene
from stats_tracker import StatsTracker
from config import Config
from output_schemas import NovelOutline

# Mock LLM for testing
class MockLLM:
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, *args, **kwargs):
        if self.output_type == "outline":
            # Return a simple outline JSON
            outline_json = {
                "title": "Test Novel",
                "author": "Test Author",
                "genre": "Test Genre",
                "acts": [
                    {
                        "number": 1,
                        "title": "Act 1",
                        "scenes": [
                            {
                                "number": 1,
                                "description": "Test scene 1 description"
                            },
                            {
                                "number": 2,
                                "description": "Test scene 2 description"
                            }
                        ]
                    }
                ]
            }
            return json.dumps(outline_json)
        elif self.output_type == "scene":
            return "Test scene content generated at " + str(os.popen("date").read().strip())
        elif self.output_type == "summary":
            return "Test summary content generated at " + str(os.popen("date").read().strip())
        else:
            return "Unknown output type"

# Patch the outline generation function to use mock data
import novel_pipeline
original_generate_novel_outline = novel_pipeline.generate_novel_outline

def mock_generate_novel_outline(llm, outliner_prompt, story_desc):
    # Create a simple outline for testing
    acts = []
    for act_num in range(1, 2):  # Just one act for simplicity
        scenes = []
        for scene_num in range(1, 3):  # Two scenes per act
            scenes.append({
                "number": scene_num,
                "description": f"Test scene {scene_num} description for act {act_num}"
            })
        acts.append({
            "number": act_num,
            "title": f"Act {act_num}",
            "scenes": scenes
        })
    
    outline_data = {
        "title": "Test Novel",
        "author": "Test Author",
        "genre": "Test Genre",
        "acts": acts
    }
    return NovelOutline.parse_obj(outline_data)

# Replace the real function with our mock for testing
novel_pipeline.generate_novel_outline = mock_generate_novel_outline

# Create mock LLMs
scene_llm = MockLLM("scene")
summary_llm = MockLLM("summary")

# Set up config
config = Config()

print("Testing novel pipeline with mocked components...")

# Test the run_novel_pipeline function
print("\nRunning pipeline in outline-only mode...")
outline, stats = run_novel_pipeline(scene_llm, summary_llm, config, outline_only=True)

print("\nOutline generated:")
print(outline.format_readable())

print("\nStats after outline generation:")
stats.print_statistics()

# Test the run_novel_pipeline function with scene generation
print("\nRunning pipeline with scene generation for a single scene...")
outline, stats = run_novel_pipeline(scene_llm, summary_llm, config, outline_only=False)

print("\nStats after full pipeline:")
stats.print_statistics()

# Restore the original function
novel_pipeline.generate_novel_outline = original_generate_novel_outline

print("\nTest complete!")