import os

class Config:
    path_to_prompts = os.path.join(os.path.abspath(__file__), 'sys_messages')
    plot_generator_prompt = os.path.join(path_to_prompts, 'plot_generator.txt')
