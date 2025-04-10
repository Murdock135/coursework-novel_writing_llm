import os

class Config:
    project_dir = os.path.dirname(__file__)
    path_to_prompts = os.path.join(os.path.abspath(project_dir), 'sys_messages')
    plot_generator_prompt = os.path.join(path_to_prompts, 'plot_generator.txt')
    
    # path to story description
    story_description = "data/story.txt"

    # novel metadata
    genre = "historical fiction"
    tone = "gloomy and analytical"
    main_character = "May"
    themes = ["betrayal", "existential crises", "illusion of the light at the end of the tunnel"]
    authors_message = None

    # output paths
    plot_outline_path = 'data/plot_outline.toml'
    scenes_path = 'data/scene_summaries'
    character_sheet_path = 'data/character_sheet.txt'

    # interaction settings
    use_interactive_decisions = False

    def get_novel_metadata(self):
        return {
            "genre": self.genre,
            "tone": self.tone,
            "main_character": self.main_character,
            "themes": self.themes,
            "authors_message": self.authors_message
        }

    def get_output_paths(self):
        return {
            "plot_outline_path": self.plot_outline_path,
            "scenes_path": self.scenes_path,
            "character_sheet_path": self.character_sheet_path
        }
