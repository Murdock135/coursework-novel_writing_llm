import os
import datetime
import toml
from utilities import io

novel_metadata_example_string = """
    story_description = "Your story description here."
    genre = "Your genre here."
    tone = "Your tone here."
    main_character_name = "Your main character here."
    themes = ["Your theme 1", "Your theme 2"]
    authors_message (optional) = "Your message to the author here."  
"""

class Config:
    def __init__(self, test=False):
        # Define project and data directories
        self.project_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.project_dir, 'data')

        # Define novel directory (adjust for testing if needed)
        time = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        self.novel_dir = os.path.join(self.data_dir, (f"novel_{time}" if not test else f"test_novel_{time}"))

        # Define novel metadata paths
        self.usr_novel_metadata_path = os.path.join(self.project_dir, 'novel_metadata.toml')
        self.novel_metadata_path = os.path.join(self.novel_dir, 'novel_metadata.toml')

        # Prompts paths
        self.usr_path_to_prompts = os.path.join(self.project_dir, 'sys_messages')
        self.outliner_prompt_path = os.path.join(self.usr_path_to_prompts, 'outliner_prompt.txt')
        self.scene_writer_prompt_path = os.path.join(self.usr_path_to_prompts, 'scene_writer_prompt.txt')
        self.scene_summarizer_prompt_path = os.path.join(self.usr_path_to_prompts, 'scene_summarizer_prompt.txt')
        self.diversity_assessor_prompt_path = os.path.join(self.usr_path_to_prompts, 'diversity_assessor_prompt.txt')
        self.path_to_prompts = os.path.join(self.novel_dir, 'sys_messages')

        # output paths
        self.path_to_output = os.path.join(self.novel_dir, 'output')
        self.outline_path = os.path.join(self.path_to_output, 'outline.txt')
        self.scene_summaries_path = os.path.join(self.path_to_output, 'scene_summaries')
        self.scenes_path = os.path.join(self.path_to_output, 'scenes')
        self.diversity_assessment_path = os.path.join(self.path_to_output, 'diversity_assessments')
        
        # Default Novel metadata
        self.default_genre = "Any"
        self.default_tone = "Neutral"
        self.default_main_character_name = "Alice"
        self.default_themes = ["Adventure", "Friendship", "Self-discovery"]
        self.default_authors_message = None

        # Create necessary directories
        print("Creating directories...")
        self._create_directories()

        # Load system prompts
        print("Loading system prompts from 'sys_messages/'...")
        self.prompts = self.load_prompts()

        # Generate a TOML file with novel metadata
        self.novel_metadata: dict = self.load_novel_metadata(self.usr_novel_metadata_path)
        self.save_novel_metadata(self.novel_metadata)

        self.config_complete_msg = f"""
        Configuration complete!
        - The novel will be saved in {self.novel_dir}.
        - The novel metadata is saved in {self.novel_metadata_path}.
        - The system prompts are saved in {self.path_to_prompts}.
        - The scene contents will be saved in {self.scenes_path}.
        - The scene summaries will be saved in {self.scene_summaries_path}.
        - The diversity assessments will be saved in {self.diversity_assessment_path}.
        """
        print(self.config_complete_msg)

        
    def _create_directories(self):
        """Create all required directories."""
        directories = [
            self.data_dir,
            self.novel_dir,
            self.usr_path_to_prompts,
            self.path_to_prompts,
            self.path_to_output,
            self.scene_summaries_path,
            self.scenes_path,
            self.diversity_assessment_path
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if not os.path.exists(directory):
                print(f"Directory created at: {directory}")

    def get_output_paths(self) -> dict:
        """Return a dictionary with paths to output directories."""
        return {
            'novel_dir': self.novel_dir,
            'outline': self.outline_path,
            'scenes': self.scenes_path,
            'scene_summaries': self.scene_summaries_path,
            'diversity_assessments': self.diversity_assessment_path
        }

    def load_novel_metadata(self, novel_metadata_path):
        """Load novel metadata from a TOML file."""

        if os.path.exists(novel_metadata_path):
            with open(novel_metadata_path, 'r') as f:
                novel_metadata = toml.load(f)

        else:
            while True:
                user_input = input(
                    f"The file {novel_metadata_path} does not exist. Do you want to use default values? (y/n): "
                ).strip().lower()

                if user_input in ['y', 'yes']:
                    print("Using default metadata...")
                    novel_metadata = {
                        "story_description": self.default_genre,
                        "genre": self.default_genre,
                        "tone": self.default_tone,
                        "main_character_name": self.default_main_character_name,
                        "themes": self.default_themes,
                        "authors_message": self.default_authors_message,
                    }
                    break
                elif user_input in ['n', 'no']:
                    raise FileNotFoundError(f"Create a novel metadata file at {novel_metadata_path} with the \
                                             following format:\n{novel_metadata_example_string}")
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")
                
        return novel_metadata
                
    def save_novel_metadata(self, novel_metadata):
        """Save novel metadata within the novel directory."""
        with open(self.novel_metadata_path, 'w') as f:
            toml.dump(novel_metadata, f)
        print(f"Novel metadata saved to {self.novel_metadata_path}")

    def load_prompts(self):
        """Load system prompts from a specified directory.
        """
        prompts = {
            'outliner_prompt': io.load_text(self.outliner_prompt_path),
            'scene_writer_prompt': io.load_text(self.scene_writer_prompt_path),
            'scene_summarizer_prompt': io.load_text(self.scene_summarizer_prompt_path),
            'diversity_assessor_prompt': io.load_text(self.diversity_assessor_prompt_path)
        }
        return prompts


