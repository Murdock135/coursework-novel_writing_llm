import os
import sys
sys.path.append('..')
from novel_pipeline import process_scene
from stats_tracker import StatsTracker
from config import Config

# Define mock classes for testing
class MockLLM:
    def __call__(self, prompt):
        return "Test content generated at " + str(os.popen("date").read().strip())

class MockScene:
    def __init__(self):
        self.description = "Test scene description"

# Set up test environment
config = Config()
stats = StatsTracker()

# Use actual directories from config
scenes_dir = os.path.join(config.project_dir, config.scenes_path)
summaries_dir = os.path.join(config.project_dir, config.scene_summaries_path)

print("Using existing directories:")
print(f"- Scenes: {scenes_dir}")
print(f"- Summaries: {summaries_dir}")

# Test the process_scene function to ensure it overwrites existing files
print("\nRunning first test...")
process_scene(
    act_index=1,
    scene_index=1,
    scene=MockScene(),
    scene_llm=MockLLM(),
    summary_llm=MockLLM(),
    scene_prompt="Write scene",
    summary_prompt="Summarize scene",
    scenes_dir=scenes_dir,
    summaries_dir=summaries_dir,
    stats_tracker=stats
)

print("\nWaiting 2 seconds...")
import time
time.sleep(2)

print("\nRunning second test - should overwrite existing files...")
process_scene(
    act_index=1,
    scene_index=1,
    scene=MockScene(),
    scene_llm=MockLLM(),
    summary_llm=MockLLM(),
    scene_prompt="Write scene",
    summary_prompt="Summarize scene",
    scenes_dir=scenes_dir,
    summaries_dir=summaries_dir,
    stats_tracker=stats
)

# Check contents of the files to see if they were overwritten
from utilities.io import get_scene_path, load_text

scene_file_path = get_scene_path(1, 1, scenes_dir, is_summary=False)
summary_file_path = get_scene_path(1, 1, summaries_dir, is_summary=True)

print("\nScene file content:")
print(load_text(scene_file_path))

print("\nSummary file content:")
print(load_text(summary_file_path))

print("\nStats:")
stats.print_statistics()