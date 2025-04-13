from langchain_core.prompts import ChatPromptTemplate
from output_schemas import DiversityAssessment
from langchain_core.output_parsers import PydanticOutputParser
from utilities.io import load_text
import random
import os

def assess_diversity(current_scene, samples, llm, prompt_path, output_schema):
    parser = PydanticOutputParser(pydantic_object=output_schema)    
    
    # Load prompt from file
    prompt_text = load_text(prompt_path)
    
    prompt = ChatPromptTemplate(
             [('system', prompt_text),
             ('user', '{current_scene}')
             ]).partial(
                     format_instructions=parser.get_format_instructions(),
                     past_scenes=samples
                     )
   
    chain = prompt | llm | parser
    response: DiversityAssessment = chain.invoke({'current_scene':current_scene})
    return response

def sample_text(filepath, sample_size=5):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) <= sample_size:
            return ''.join(lines) # return all lines if file has fewer lines than sample size
    return ''.join(random.sample(lines, sample_size))

def get_samples(scene_dir):
    samples = []
    for scene_file in os.listdir(scene_dir):
        full_path = os.path.join(scene_dir, scene_file)
        if os.path.isfile(full_path):
            scene_sample = sample_text(full_path)
            samples.append(scene_sample)
    
    print(f"Loaded {len(samples)} scene samples for diversity assessment")
    return samples


if __name__ == "__main__":
    pass
