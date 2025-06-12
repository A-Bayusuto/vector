from openai import AzureOpenAI
import pandas as pd
import os
import re

class ChatBuilder:
    def __init__(self, client, 
                 sys_content="You are a help AI answering the user's questions", 
                    assistance_list=[], temperature=0.2):
        self.client = client
        self.deployment = None
        self.user_content = None
        self.assistant_content = None
        self.sys_content = {
            "role": "system",
            "content": sys_content
        }
        self.assistance_list = assistance_list  # must add in ({"role": "user", "content": user_content}, {"role": "user", "content": user_content}) format
        self.temperature = temperature
        self.messages = []

    def set_deployment(self, deployment):
        self.deployment = deployment

    def set_client(self, client):
        self.client = client

    def set_system(self, sys_content):

        self.sys_content = {
            "role": "system",
            "content": sys_content
        }
        
    def set_assistance(self, assistant_content):
        """
        Set the user's message.
        :param user_message: The content of the user input as a string.
        """
        self.assistant_content = {
            "role": "assistant",
            "content": assistant_content
        }
    
    def create_assistant_message(self, assistant_content):
        assistant_message = {
            "role": "assistant",
            "content": assistant_content
        }
        return assistant_message

    def set_user(self, user_content):
        """
        Set the user's message.
        :param user_message: The content of the user input as a string.
        """
        self.user_content = {
            "role": "user",
            "content": user_content
        }

    def create_user_message(self, user_content):
        user_message = {
            "role": "user",
            "content": user_content
        }
        return user_message
    
    def add_assistance_list(self, user_content, assistant_content):
        self.assistance_list.append((user_content, assistant_content))

    def set_temperature(self, temperature):
        self.temperature = temperature
    
    def message_continuation(self, user_content):
        self.messages.append(user_content)
        return self.messages
    
    def output_formatter(output):
        # Regular expression to match numbers followed by '.'
        pattern = r'\b\d+\.'

        # Find all matches
        matches = re.finditer(pattern, output)

        # Extract indices
        indices = [match.start() for match in matches]

        result = output
        for i, index in enumerate(indices):
            adjusted_index = index + i 
            result = result[:adjusted_index] + "\n" + result[adjusted_index:]

        return result
    
    def format_list(self, text, list_pattern=r"\d+\..*?(?=\s\d+\.|$)"):
        # Regex to match numbered list patterns
        # list_pattern = r"(\d+\.\s[^.\d]+(?:\"|\.))"
        
        # Find all matches for numbered list items
        matches = re.findall(list_pattern, text)

        if not matches:
            return text  # Return the original text if no list is found

        # Create a nicely formatted string with new lines
        formatted_list = "<br>".join([item.strip() for item in matches])

        # Replace the original list in the text with the nicely formatted version
        non_list_part = re.split(list_pattern, text)[0]  # Text before the list starts
        formatted_text = f"{non_list_part.strip()}<br><br>{formatted_list}"

        return formatted_text.strip()


    def chat_completion(self):  # chain of thought
        try:
            new_messages = self.message_continuation(self.user_content)
            # print("new_messages: ", new_messages)
            # return
            # print(self.sys_content)
            print('temp: ', self.temperature)
            print('sys_content: ', self.sys_content)
            print('messages: ', self.messages)
            response = self.client.chat.completions.create(
                model= self.deployment,
                messages= new_messages,
                temperature= self.temperature
            )
            output = response.choices[0].message.content
            print("output1: " + output)
            output2 = self.format_list(output)
            print("output2:\n")
            print(output2)
            output_message = self.create_assistant_message(output2)
            self.messages.append(output_message)
            return output2
            
        
        except Exception as e:
            print(f"Error: {e}")
            return None

    def few_shot_prompting(self, **kwargs):
        system_content = kwargs.get("system_content", "Generic openai helper")
        self.set_system(system_content)
        self.messages.append(self.set_system)

        template_content = list(kwargs.get("system_content", "Generic openai helper"))
        # should be list of tuples with user ans assistant prompts
        for x in template_content:
            user_m = self.create_user_message(x[0])
            assis_m = self.create_assistant_message(x[1])
            self.messages.append(user_m)
            self.messages.append(assis_m)
        """ messages should be in"
        " { sys:....  "
        "   user:..."
        "   assis:.."
        "   user:... etc"
        "}"""
        temperature = kwargs.get("temperature")
        if temperature:
            self.set_temperature(temperature)
            
        return self.chat_completion()
    
    def chain_of_thought_prompting(self, **kwargs):
        system_content = kwargs.get("system_content", "Generic openai helper")
        self.set_system(system_content)
        self.messages.append(self.set_system)

        chain_of_thought = kwargs.get("chain_of_thought", [])
        message = ""
        for x in list(chain_of_thought):
            message += x
        self.messages.append(message)
        return self.chat_completion()

    def judgement_prompting(self, **kwargs):
        # TODO
        return None

    def CAG(self, system, context, question):  # Cache Augmented Generation
        system_content = system
        self.set_system(system_content)
        self.messages.append(self.set_system)
        # context is path to file assume excel
        file = pd.read_excel(context)
        file_str = file.to_string(index=False)  # Converts DataFrame to a human-readable string
        user_mes = self.create_user_message(file_str)
        user_mes += f"\n \n {question}"
        self.set_system(user_mes)
        return self.chat_completion()
    
    def keep_last_10(self):
        new_messages = []
        system_messge = [x for x in self.messages if x.get("role") == 'system']
        non_sys_message = [x for x in self.messages if x.get("role") != 'system']
        new_messages = system_messge[:1] + non_sys_message[-20:]
        print('===============')
        print(new_messages)
        print('===============')
        self.messages = new_messages


    def save_messages_to_file(self, file_name):
        folder_name = "chat_history"
        file_path = os.path.join(folder_name, file_name)
        print(file_path)

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                for message in self.messages:
                    file.write(str(message) + "\n")
            print(f"Messages saved successfully to {file_path}")
        except Exception as e:
            print(f"An error occurred while saving messages: {e}")

    def load_messages_from_file(self, file_name):
        folder_name = "chat_history"
        file_path = os.path.join(folder_name, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.messages = [eval(line.strip()) for line in file.readlines()]
            print(f"Messages loaded successfully from {file_path}")
        except Exception as e:
            print(f"An error occurred while loading messages: {e}")


            
