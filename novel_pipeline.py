from novel_outliner import generate_outline
from scene_writer import write_scene
from scene_summary_generator import generate_scene_summary
from scene_diversity_assessor import assess_diversity, get_samples
from utilities import retrieval, io
from output_schemas import NovelOutline, DiversityAssessment

def run_novel_pipeline(
        novel_metadata,
        outliner_llm,
        scene_writer_llm,
        summarizer_llm,
        diversity_assessor_llm,
        prompts_dict,
        output_paths_dict,
        max_retries=3,  # Add max_retries as a parameter
        stats_tracker=None,
):
    print("Generating novel outline...")
    outline: NovelOutline = generate_outline(outliner_llm, prompts_dict['outliner_prompt'], novel_metadata, None if stats_tracker is None else stats_tracker)
    print(outline.format_readable())
    stats_tracker.increment_llm_calls() if stats_tracker else None

    print(50 * "=")
    for act_index, act in enumerate(outline.acts, 1):
        for scene_index, scene in enumerate(act.scenes, 1):
            print(f"Generating scene {scene_index} in act {act_index}...")

            # if this is the first scene, write it without retrieving past context
            if scene_index == 1:
                scene_content = write_scene(scene_writer_llm, prompts_dict['scene_writer_prompt'], scene.description, novel_metadata)
                stats_tracker.increment_llm_calls() if stats_tracker else None
                stats_tracker.increment_scenes() if stats_tracker else None


            # else use past summaries as relevant context and an assessor to assess diversity and keep rewriting until satisfactory
            else:
                # Load summaries and retrieve context
                summaries = retrieval.load_summaries(output_paths_dict['scene_summaries'])
                prefix_context = retrieval.get_relevant_context(scene.description, summaries)

                retry = 0
                while retry < max_retries:
                    # Write the scene
                    scene_content = write_scene(
                        scene_writer_llm,
                        prompts_dict['scene_writer_prompt'],
                        scene.description,
                        novel_metadata,
                        prefix_context,
                    )
                    stats_tracker.increment_llm_calls() if stats_tracker else None

                    # Assess diversity
                    samples = get_samples(output_paths_dict['scenes'])
                    assessment: DiversityAssessment = assess_diversity(
                        current_scene=scene_content,
                        samples=samples,
                        llm=diversity_assessor_llm,
                        prompt_text=prompts_dict['diversity_assessor_prompt'],
                        output_schema=DiversityAssessment,
                    )
                    stats_tracker.increment_llm_calls() if stats_tracker else None

                    # Check if the scene is diverse enough
                    if assessment.is_diverse_enough:
                        break
                    else:
                        print("Diversity assessment failed. Here is the analysis:")
                        print(assessment.analysis)
                        print(assessment.stylistic_diversity)
                        print(assessment.thematic_depth)
                        print(assessment.tonal_variation)
                        print(assessment.guidance)

                        # Rewrite the scene with guidance
                        scene_content = write_scene(
                            scene_writer_llm,
                            prompts_dict['scene_writer_prompt'],
                            scene.description,
                            novel_metadata,
                            prefix_context,
                            assessment.guidance
                        )
                        retry += 1
                        print(f"Retrying scene {scene_index} in act {act_index} for diversity...")

                        stats_tracker.increment_llm_calls() if stats_tracker else None
                        stats_tracker.increment_diversity_assessment_failures() if stats_tracker else None
                        stats_tracker.increment_scenes() if stats_tracker else None

                    if retry == max_retries:
                        print(f"Max retries reached for scene {scene_index} in act {act_index}. Proceeding with the last attempt.")

            # Generate scene summary
            scene_summary = generate_scene_summary(
                summarizer_llm,
                prompts_dict['scene_summarizer_prompt'],
                scene_content,
                novel_metadata
            )
            stats_tracker.increment_llm_calls() if stats_tracker else None
            stats_tracker.increment_summaries() if stats_tracker else None

            # Pretty print scene and scene summary
            io.pretty_print(act_index, scene_index, scene_content)
            io.pretty_print(act_index, scene_index, scene_summary, is_summary=True)

            # Save the scene and summary
            io.save_content_to_file(
                content=scene_content,
                act_num=act_index,
                scene_num=scene_index,
                output_dir=output_paths_dict['scenes'],
                is_summary=False
            )
            io.save_content_to_file(
                content=scene_summary,
                act_num=act_index,
                scene_num=scene_index,
                output_dir=output_paths_dict['scene_summaries'],
                is_summary=True
            )
            print(f"Scene {scene_index} in act {act_index} generated and saved.")
