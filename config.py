import os
import datetime
import toml

class Config:
    def __init__(self, test=False):
        # Define project and data directories
        self.project_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.project_dir, 'data')

        # Define novel directory (adjust for testing if needed)
        time = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        self.novel_dir = os.path.join(self.data_dir, f"novel_{time}")
        if test:
            self.novel_dir = os.path.join(self.data_dir, f"test_novel_{time}")

        # Define paths
        self.path_to_prompts = os.path.join(self.novel_dir, 'sys_messages')
        self.path_to_output = os.path.join(self.novel_dir, 'output')
        self.scene_summaries_path = os.path.join(self.path_to_output, 'scene_summaries')
        self.scenes_path = os.path.join(self.path_to_output, 'scenes')
        self.diversity_assessment_path = os.path.join(self.path_to_output, 'diversity_assessments')
        self.novel_metadata_path = os.path.join(self.novel_dir, 'novel_metadata.toml')

        # Novel metadata
        self.genre = "historical fiction"
        self.tone = "gloomy and analytical"
        self.main_character = "May"
        self.themes = ["betrayal", "existential crises", "illusion of the light at the end of the tunnel"]
        self.authors_message = None

        # Create necessary directories
        self._create_directories()

        # Generate a TOML file with novel metadata
        self._save_novel_metadata()

    def _create_directories(self):
        """Create all required directories."""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.novel_dir, exist_ok=True)
        os.makedirs(self.path_to_prompts, exist_ok=True)
        os.makedirs(self.path_to_output, exist_ok=True)
        os.makedirs(self.scene_summaries_path, exist_ok=True)
        os.makedirs(self.scenes_path, exist_ok=True)
        os.makedirs(self.diversity_assessment_path, exist_ok=True)

    def _save_novel_metadata(self):
        """Save novel metadata to a TOML file."""
        novel_metadata = {
            "genre": self.genre,
            "tone": self.tone,
            "main_character": self.main_character,
            "themes": self.themes,
            "authors_message": self.authors_message,
        }
        with open(self.novel_metadata_path, 'w') as f:
            toml.dump(novel_metadata, f)

