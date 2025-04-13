import os

class Config:
    project_dir = os.path.dirname(__file__)
    path_to_prompts = os.path.join(os.path.abspath(project_dir), 'sys_messages')
    plot_generator_prompt = os.path.join(path_to_prompts, 'plot_generator.txt')
    scene_writer_prompt = os.path.join(path_to_prompts, 'scene_writer.txt')
    scene_summary_generator_prompt = os.path.join(path_to_prompts, 'scene_summary_generator.txt')
    diversity_assessor_prompt = os.path.join(path_to_prompts, 'scene_diversity_assessor.txt')
    
    # path to story description
    story_description_path = "data/story.txt"

    # novel metadata
    genre = "historical fiction"
    tone = "gloomy and analytical"
    main_character = "May"
    themes = ["betrayal", "existential crises", "illusion of the light at the end of the tunnel"]
    authors_message = None

    # output paths
    plot_outline_path = 'data/plot_outline.toml'
    scene_summaries_path = 'data/scene_summaries'
    scenes_path = 'data/scenes'
    character_sheet_path = 'data/character_sheet.txt'
    diversity_assessment_path = 'data/diversity_assessment.txt'
    
    # test output paths
    test_path = 'data/test'
    test_scenes_path = 'data/test/scenes'
    test_summaries_path = 'data/test/summaries'

    # interaction settings
    use_interactive_decisions = False

    def __init__(self):
        # Ensure all necessary directories exist
        self._ensure_directories_exist([
            os.path.dirname(self.story_description_path),
            os.path.dirname(self.plot_outline_path),
            self.scene_summaries_path,
            self.scenes_path,
            os.path.dirname(self.character_sheet_path),
            os.path.dirname(self.diversity_assessment_path),
            self.test_path,
            self.test_scenes_path,
            self.test_summaries_path
        ])

    def _ensure_directories_exist(self, directories):
        """Ensure that all directories in the list exist."""
        for directory in directories:
            full_path = os.path.join(self.project_dir, directory)
            os.makedirs(full_path, exist_ok=True)

    def get_novel_metadata(self):
        return {
            "genre": self.genre,
            "tone": self.tone,
            "main_character": self.main_character,
            "themes": self.themes,
            "authors_message": self.authors_message
        }
    
    def get_scenes_dir(self):
        """Get the full path to the scenes directory and ensure it exists."""
        scenes_dir = os.path.join(self.project_dir, self.scenes_path)
        os.makedirs(scenes_dir, exist_ok=True)
        return scenes_dir
    
    def get_summaries_dir(self):
        """Get the full path to the scene summaries directory and ensure it exists."""
        summaries_dir = os.path.join(self.project_dir, self.scene_summaries_path)
        os.makedirs(summaries_dir, exist_ok=True)
        return summaries_dir

