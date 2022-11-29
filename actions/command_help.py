import time


class CommandHelp:
    def __init__(self, help_lines: list[str], reset_time: int = 1.5):
        #A list containing all the help lines.
        self.help_lines = help_lines
        #After how long the 
        self.reset_time = reset_time

        self.current_reset_time = 0
        self.current_line = 0


    #Gets the help line corresponding to the current index, then increments it by one.
    def get_help_line(self) -> str:
        line_count = len(self.help_lines)
        old_line = self.current_line
        self.current_reset_time = time.time()

        #We check if we are on the end of the help lines, if so we wrap around.
        if self.current_line == line_count - 1:
            self.current_line = 0
        #Otherwise we just increment the counter.
        else:
            self.current_line += 1

        #Return the appropriate help line with a counter.
        return f"Command help {old_line + 1}/{line_count}: {self.help_lines[old_line]}"


    def help_line_handler(self) -> None:
        #If the time after the last press exceeds the reset time we reset the line counter.
        if time.time() >= self.current_reset_time + self.reset_time:
            self.current_line = 0
