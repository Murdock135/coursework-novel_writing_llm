import os

class Config:
    project_dir = os.path.dirname(__file__)
    path_to_prompts = os.path.join(os.path.abspath(project_dir), 'sys_messages')
    plot_generator_prompt = os.path.join(path_to_prompts, 'plot_generator.txt')

