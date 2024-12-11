import os
import json
import yaml
import argparse 
import modules

from utils.utils_main import *
from modules.storymanager import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_type', type=str, default='gpt-4o-mini')
    parser.add_argument('--resume_dir', type=str, default='./outputs/2024-11-03_story_container.json')
    parser.add_argument('--output_dir', type=str, default='./outputs')
    parser.add_argument('--api_key', type=str, default=None)
    args = parser.parse_args()

    # load configs
    configs = load_config(args, config_path="./configs/configs.yaml", api_key_path="./configs/api_key.yaml")
    if configs is None:
        exit()

    # STEP 1: init or resume a story teller
    story_teller = step_1_init_or_resume(args, configs)

    # STEP 2: get key words, a hint or other story prompt
    user_hint = step_2_get_hint(story_teller)

    # STEP 3: generate a story outline
    outline = step_3_generate_outline(story_teller, user_hint)

    # STEP 4: get story style
    story_style = step_4_generate_story_style(story_teller, outline)

    # STEP 5: generate roles
    characters = step_5_generate_characters(story_teller, outline, story_style)

    # STEP 6: generate chapter scripts
    chapter_scripts = step_6_generate_chapter_scripts(story_teller, outline, story_style, characters)

    # prepare to tell
    story_teller.pepare_to_tell()

    # interact with story
    current_chapter = story_teller.story_container["current_chapter"]
    current_stage = story_teller.story_container["current_stage"]
    need_resume = (current_chapter > 1) or (current_stage > 1)

    for chapter_num in range(1, configs["MAX_CHAPTERS"] + 1):
        for stage_num in range(1, configs["MAX_STAGES"] + 1):

            if need_resume:
                chapter_num = story_teller.story_container["current_chapter"]
                stage_num = story_teller.story_container["current_stage"]
                need_resume = False

            print(f"============= 当前章节{chapter_num}-{stage_num}: {story_teller.story_container["chapter_scripts"][chapter_num-1]["标题"]} =============")

            story_teller.story_container["current_chapter"] = chapter_num
            story_teller.story_container["current_stage"] = stage_num

            current_stage_story, current_stage_choice = story_teller.generate_one_stage_story(chapter_num=chapter_num, stage_num=stage_num)
            print("="*50)
            print(current_stage_story)
            if current_stage_choice is not None:
                for i, choice in enumerate(current_stage_choice):
                    print(f"{"ABCD"[i]}: {choice}")
                need_to_choice = True
                while(need_to_choice):
                    your_choice = input("Enter your choice: ")
                    if your_choice.upper() in ["A", "B", "C", "D"]:
                        chosed_action = current_stage_choice["ABCD".index(your_choice.upper())]
                        print(f"当前行动：{chosed_action}")
                        story_teller.story_container["previous"].append(chosed_action)
                        need_to_choice = False

            story_teller.update_container()


if __name__=='__main__':
    main()