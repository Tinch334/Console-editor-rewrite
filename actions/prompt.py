#This class has a basic prompt that can be easily accessed.
class Prompt:
    def __init__(self, default_prompt: str, prompt_reset_time: int):
        #Prompt to be used normally.
        self.default_prompt = default_prompt
        #How long a non default prompt may stay, in seconds.
        self.prompt_reset_time = prompt_reset_time

        self.current_prompt = self.default_prompt
        self.current_reset_time = 0


    #Returns the current prompt.
    def get_prompt(self) -> str:
        return self.current_prompt


    #Changes the current prompt.
    def change_prompt(self, new_prompt: str) -> None:
        self.current_prompt = new_prompt
        self.current_reset_time = time.time()


    #Checks if the prompt should be reset to the default prompt.
    def prompt_handler(self) -> None:
        if time.time() >= self.current_reset_time + self.prompt_reset_time:
            self.current_prompt = self.default_prompt