import os
import json
import yaml
import argparse 
import modules

from utils.utils_main import load_config

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

    if (args.resume_dir is not None) and (os.path.exists(args.resume_dir)):
        # resume story if given
        story_container = json.load(open(args.resume_dir))
        story_teller = modules.Storyteller(args, configs, story_container=story_container)
    else:
        # init a new story teller
        story_teller = modules.Storyteller(args, configs)

    # init a new story hint
    if "story_hint" in story_teller.story_container:
        user_hint = story_teller.story_container["story_hint"]
    else:
        user_hint = input("Enter some hint for the story you like: ")
        story_teller.story_container["story_hint"] = user_hint
        story_teller.update_container()

    # get outline
    if "outline" not in story_teller.story_container:
        outline = story_teller.generate_outline(user_hint=user_hint)
        print("="*50)
        print(f"Story Outline: {outline}")

    # get story style
    if "story_style" not in story_teller.story_container:
        story_style = story_teller.generate_story_style(outline=outline)
        print("="*50)
        print(f"Story Style: {story_style}")

    # get characters
    if "characters" not in story_teller.story_container:
        characters = story_teller.generate_characters(outline=outline, story_style=story_style)
        print("="*50)
        print(f"Story Characters: {characters}")

    # get chapter outlines
    if "chapter_scripts" not in story_teller.story_container:
        chapter_scripts = story_teller.generate_chapter_scripts(outline=outline, story_style=story_style, characters=characters)
        print("="*50)
        print(f"Chapter Scripts: {chapter_scripts}")

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