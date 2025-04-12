from config import Config
from langchain_core.prompts import ChatPromptTemplate
from output_schemas import DiversityAssessment
from langchain_core.output_parsers import PydanticOutputParser
from utilities.io import load_text
import random
import os

def assess_diversity(current_scene, samples, llm, prompt, output_schema):
    parser = PydanticOutputParser(pydantic_object=output_schema)    

    prompt= ChatPromptTemplate(
             [('system', prompt),
             ('user_message', '{current_scene}')
             ]).partial(
                     format_instructions=parser.get_format_instructions(),
                     past_scenes=samples
                     )
   
   chain = prompt | llm | parser
   response = chain.invoke({'current_scene':current_scene})
   return response

def sample_text(filepath, sample_size=5):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) <= sample_size:
            return ''.join(lines) # return all lines if file has fewer lines than sample size
    return ''.join(random.sample(lines, sample_size))

def get_samples(scene_dir):
    samples = []
    for scene_path in os.listdir(scene_dir):
        scene_sample = sample_text(scene_path)
        samples.append(scene_sample)
    
    return samples


if __name__ == "__main__":
    pass
