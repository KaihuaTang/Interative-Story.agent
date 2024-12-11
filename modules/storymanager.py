import os
import json
import yaml
import argparse 
import modules


def step_1_init_or_resume(args, configs):
    # initialize a new story or resume from an existing story
    if (args.resume_dir is not None) and (os.path.exists(args.resume_dir)):
        # resume from an existing story
        print(f"Resume from {args.resume_dir}")
        story_container = json.load(open(args.resume_dir))
        story_teller = modules.Storyteller(args, configs, save_path=args.resume_dir, story_container=story_container)
    else:
        # init a new story
        print("Initialize a new story")
        story_teller = modules.Storyteller(args, configs)
    return story_teller


def step_2_get_hint(story_teller):
    if "story_hint" in story_teller.story_container:
        user_hint = story_teller.story_container["story_hint"]
    else:
        user_hint = input("Enter some hint for the story you like: ")
        story_teller.story_container["story_hint"] = user_hint
        story_teller.update_container()
    return user_hint


def step_3_generate_outline(story_teller, user_hint):
    # get outline
    if "outline" not in story_teller.story_container:
        prompt = story_teller.configs["OUTLINE_PROMPT"].format(hint = user_hint)
        outline, _ =  story_teller.chat_with_storyteller(prompt)
        if outline is not None:
            story_teller.story_container["outline"] = outline
            story_teller.update_container()
            print("="*50)
            print(f"Story Outline: {outline}")
        else:
            print("Generate Story Outline Failed Once!")
    else:
        outline = story_teller.story_container["outline"]
        print(f"resume from existing outline: {outline}")

    return outline


def step_4_generate_story_style(story_teller, outline):
    if "story_style" not in story_teller.story_container:
        prompt = story_teller.configs["STYLE_PROMPT"].format(outline = outline)
        story_style, _ =  story_teller.chat_with_storyteller(prompt)
        if story_style is not None:
            story_teller.story_container["story_style"] = story_style
            story_teller.update_container()
            print("="*50)
            print(f"Story Style: {story_style}")
        else:
            print("Generate Story Style Failed Once!")
    else:
        story_style = story_teller.story_container["story_style"]
        print(f"resume from existing story style: {story_style}")

    return story_style


def step_5_generate_characters(story_teller, outline, story_style):
    # get characters
    if "characters" not in story_teller.story_container:
        prompt = story_teller.configs["CHARACTER_PROMPT"].format(outline = outline, story_style = story_style)
        need_correct_characters = True
        while(need_correct_characters):
            characters, _ =  story_teller.chat_with_storyteller(prompt)
            characters = story_teller.string_to_dictionary(characters)
            if (characters is not None) and ("角色列表" in characters):
                need_correct_characters = False
            else:
                print("Generate Characters Failed Once!")      
        story_teller.story_container["characters"] = characters["角色列表"]
        story_teller.update_container()
        print("="*50)
        print(f"Story Characters: {characters}")
    else:   
        characters = story_teller.story_container["characters"]
        print(f"resume from existing characters: {characters}")
    
    return characters


def step_6_generate_chapter_scripts(story_teller, outline, story_style, characters):
     # get chapter outlines
    if "chapter_scripts" not in story_teller.story_container:
        prompt = story_teller.configs["CHAPTER_PROMPT"].format(outline=outline, story_style=story_style, characters=characters) 
        
        need_correct_chapters = True
        while(need_correct_chapters):
            chapter_scripts, _ =  story_teller.chat_with_storyteller(prompt)
            chapter_scripts = story_teller.string_to_dictionary(chapter_scripts)
            if (chapter_scripts is not None) and ("章节大纲" in chapter_scripts):
                need_correct_chapters = False
            else:
                print("Generate Chapter Scripts Failed Once!")

        story_teller.story_container["chapter_scripts"] = chapter_scripts["章节大纲"]
        story_teller.update_container()
        print("="*50)
        print(f"Chapter Scripts: {chapter_scripts}")
    else:
        chapter_scripts = story_teller.story_container["chapter_scripts"]
        print(f"resume from existing chapter scripts")
    
    return chapter_scripts