import os

class Config:
    self.project_dir = os.path.dirname(__file__)
    self.path_to_prompts = os.path.join(os.path.abspath(project_dir), 'sys_messages')
    self.plot_generator_prompt = os.path.join(path_to_prompts, 'plot_generator.txt')
    
    # novel metadata
    self.genre = "historical fiction"
    self.tone = "gloomy and analytical"
    self.main_character = "May"
    self.themes = ["betrayal", "existential crises", "illusion of the light at the end of the tunnel"]
    self.authors_message = None

    # output paths
    self.plot_outline_path = 'data/plot_outline.toml'
    self.scenes_path = 'data/scene_summaries'
    self.character_sheet = 'data/character_sheet'

    # interaction settings
    self.use_interactive_decisions = False

    @staticmethod
    def get_novel_metadata():
        return {
            "genre": Config.genre,
            "tone": Config.tone,
            "main_character": Config.main_character,
            "themes": Config.themes,
            "authors_message": Config.authors_message
        }

    @staticmethod
    def get_output_paths():
        return {
            "plot_outline_path": Config.plot_outline_path,
            "scenes_path": Config.scenes_path,
            "character_sheet": Config.character_sheet
        }
