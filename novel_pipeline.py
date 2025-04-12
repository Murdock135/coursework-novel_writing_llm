from outline_generator import generate_outline
from scene_writer import write_scene
from scene_summary_generator import generate_scene_summary
from scene_diversity_assessor import assess_diversity
from utilities.retrieval import SceneRetriever
from output_schemas import NovelOutline, DiversityAssessment

def run_novel_pipeline(
        story_description,
        novel_metadata,
        outliner_llm,
        scene_writer_llm,
        summarizer_llm,
        diversity_assessor_llm,
        retriever: SceneRetriever,
        prompt_paths_dict,
        output_paths_dict
):
    outline: NovelOutline = generate_outline(outliner_llm, prompt_paths_dict['plot'], story_description, novel_metadata)

    for act_index, act in enumerate(outline.acts, 1):
        for scene_index, scene in enumerate(act.scenes, 1):
            if scene_index == 1: # if this is the first scene, write it without retrieving past context
                scene = write_scene(scene_writer_llm, prompt_paths_dict['scene'], scene.description, novel_metadata)
            else:
                summaries = retriever.load_summaries(output_paths_dict['summaries'])
                prefix_context = retriever.get_relevant_context()
                scene = write_scene(scene_writer_llm, prompt_paths_dict['scene'], scene.description, novel_metadata, retriever)