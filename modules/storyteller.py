import os
import json
from openai import OpenAI
from datetime import datetime


class Storyteller():
    def __init__(self, args, configs, save_path=None, story_container=None):
        self.args = args
        self.configs = configs
        self.model_type = args.model_type

        # initialize save path
        self.save_path = os.path.join(self.args.output_dir, f"{datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")}.json") if save_path is None else save_path

        # initialize story container
        self.story_container = {} if story_container is None else story_container

        # check whether the model is supported, if yes return api type
        if args.model_type in configs['MODEL2API']:
            self.api_type = configs['MODEL2API'][args.model_type]
        else:
            raise ValueError(f"Model type is not supported {args.model_type}")

        # set client according to api type
        if self.api_type == 'openai':
            self.client = OpenAI(api_key=configs["api_key"])
        else:
            raise ValueError(f"API type is not supported: {self.api_type}")
        

    def update_container(self):
        with open(self.save_path, "w", encoding="utf-8") as json_file:
            json.dump(self.story_container, json_file, ensure_ascii=False, indent=4)


    def string_to_dictionary(self, input_str):
        # Find the indices of the first '{' and last '}'
        start = input_str.find('{')
        end = input_str.rfind('}')

        try:
            # Check if both braces are found and start is before end
            if start != -1 and end != -1 and start < end:
                input_str = input_str[start:end+1]
                output_dict = json.loads(input_str)
        except:
            print(f"Fail to get correct dictionary: {input_str}")
            output_dict = None
        
        return output_dict


    def pepare_to_tell(self):
        if "previous" not in self.story_container:
            self.story_container["previous"] = []
        if "previous_prompt" not in self.story_container:
            self.story_container["previous_prompt"] = []
        if "current_chapter" not in self.story_container:
            self.story_container["current_chapter"] = 1
        if "current_stage" not in self.story_container:
            self.story_container["current_stage"] = 1


    def generate_one_stage_story(self, chapter_num, stage_num):
        # construct prompt
        current_chapter_info = self.story_container["chapter_scripts"][chapter_num - 1]

        stage_desc = self.configs[f"STAGE_DESC_{stage_num}"]
        if (stage_num == 5): 
            if (chapter_num < 5):
                stage_desc = stage_desc["open"].format(next_chapter_outline=self.story_container["chapter_scripts"][chapter_num]["剧情摘要"])
            else:
                stage_desc = stage_desc["close"] 
        
        if (stage_num < 5):
            stage_notes = self.configs["STAGE_NOTES_CONTINUE"]
        else:
            stage_notes = self.configs["STAGE_NOTES_LAST"]

        chapter_outline = current_chapter_info["剧情摘要"]
        current_character_list = current_chapter_info["出场角色"]

        story_style = self.story_container["story_style"]

        chapter_characters = []
        for character in self.story_container["characters"]:
            if character["姓名"] in current_character_list:
                chapter_characters.append(character)

        if len(self.story_container["previous"]) > 0:
            previous_story = "\n".join(self.story_container["previous"])
        else:
            previous_story = "无。"

        prompt = self.configs["STORY_PROMPT"].format(stage_desc=stage_desc,
                                                stage_notes=stage_notes, 
                                                chapter_outline=chapter_outline,
                                                story_style=story_style,
                                                chapter_characters=chapter_characters,
                                                previous_story=previous_story)

        need_to_generate = True
        while(need_to_generate):
            stage_story, _ =  self.chat_with_storyteller(prompt, storytelling=True)
            stage_story = self.string_to_dictionary(stage_story)

            if (stage_story is not None) and ("小说内容" in stage_story):
                contents = stage_story["小说内容"]
                if (stage_num < 5): 
                    choices = stage_story["剧情选择"]
                    assert len(choices) == 4
                else:
                    choices = None
                need_to_generate = False
            else:
                print("Generate Chapter Stage Story Failed Once!")
                
        self.story_container["previous"].append(contents)
        self.story_container["previous_prompt"].append(prompt)
        self.update_container()
        return contents, choices
    



    def chat_with_storyteller(self, query, history=None, storytelling=False):
        if self.api_type == 'openai':
            return self.chat_with_openai_client(query, history, storytelling)
        else:
            raise ValueError(f"Wrong API type. Query: {query}")


    def chat_with_openai_client(self, query, history, storytelling=False):

        if storytelling:
            system_prompt = self.configs["SYSTEM_PROMPT_WRITE"]
        else:
            system_prompt = self.configs["SYSTEM_PROMPT_TOOL"]

        # construct messages with history and system prompt
        if (history is not None) and (len(history) > 0):
            history.append({"role": "user", "content": query})
        else:
            history = [{"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}]
            
        # complete
        try:
            completion = self.client.chat.completions.create(
                            model=self.model_type,
                            messages=history
                        )
            response = completion.choices[0].message.content
            history.append({"role": "assistant", "content": response})
        except:
            print(f"No response from API. Query: {query}")
            response = None 
            history.pop()
        
        return response, history
            
