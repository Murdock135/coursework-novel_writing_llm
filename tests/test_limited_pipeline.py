import os
import sys
sys.path.append('..')
from novel_pipeline import process_scene, prepare_prompts, create_output_directories
from stats_tracker import StatsTracker
from config import Config
from output_schemas import NovelOutline, Act, Scene
from typing import List, Dict

# Create a config instance
config = Config()

# Initialize stats tracker
stats_tracker = StatsTracker()

# Create mock classes
class MockLLM:
    def invoke(self, prompt):
        class MockResponse:
            def __init__(self, content):
                self.content = content
                
        return MockResponse("This is mock content generated for testing purposes.")

# Use the real NovelOutline schema but with simple data
def create_test_outline():
    return NovelOutline(
        acts=[
            Act(
                scenes=[
                    Scene(description="Test scene description for limited test")
                ]
            )
        ]
    )

print("Starting limited pipeline test...")

# Create the output directories
scenes_dir, summaries_dir = create_output_directories(config)

# Generate mock outline
outline = create_test_outline()
novel_metadata = config.get_novel_metadata()

print("\nMock outline created:")
print(outline.format_readable())

# Prepare prompts
scene_prompt, summary_prompt = prepare_prompts(config, novel_metadata)
print("\nPrompts prepared")

# Process just a single scene
print("\nProcessing a single scene (act 1, scene 1)...")
error = process_scene(
    act_index=1,
    scene_index=1,
    scene=outline.acts[0].scenes[0],
    scene_llm=MockLLM(),
    summary_llm=MockLLM(),
    scene_prompt=scene_prompt,
    summary_prompt=summary_prompt,
    scenes_dir=scenes_dir,
    summaries_dir=summaries_dir,
    stats_tracker=stats_tracker
)

if error:
    print(f"Error: {error}")

# Print stats
print("\nStats after processing:")
stats_tracker.print_statistics()

from utilities.io import get_scene_path, load_text

# Check the outputs
scene_file_path = get_scene_path(1, 1, scenes_dir, is_summary=False)
summary_file_path = get_scene_path(1, 1, summaries_dir, is_summary=True)

print("\nChecking output files:")
if os.path.exists(scene_file_path):
    print(f"Scene file exists: {scene_file_path}")
    content = load_text(scene_file_path)
    print(f"Scene file length: {len(content)} characters")
    print(f"Scene preview: {content[:100]}...")
else:
    print("Scene file was not created!")

if os.path.exists(summary_file_path):
    print(f"Summary file exists: {summary_file_path}")
    content = load_text(summary_file_path)
    print(f"Summary file length: {len(content)} characters")
    print(f"Summary preview: {content[:100]}...")
else:
    print("Summary file was not created!")

print("\nTest complete!")