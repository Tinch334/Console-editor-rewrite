from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Line:
    contents: str = ""



class TextBuffer:
    def __init__(self):
        self.buffer = [Line()]

    #####USE NOTE#####
    #All the functions in this dataclass use indexes starting at zero. Furthermore when referring to the "x_pos" in a line it must be thought of
    #as if it were a cursor. What this means is that an "x_pos" of zero would be at the very start of the line, NOT the first character.


    #Adds a character in the specified position in the buffer, returns "True" if no errors occurred. To insert the character at the end of the
    #specified line leave or set "x_pos" to "None".
    def add_char(self, char: str, y_pos: int, x_pos: Optional[int] = None) -> bool:
        try:
            if x_pos == None:
                self.buffer[y_pos].contents += char
            #In case we want to insert a character at the beginning of the line.
            elif x_pos == 0:
                self.buffer[y_pos].contents = char + self.buffer[y_pos].contents
            #If we want to insert a character in the middle of the line we split the string and then insert the character.
            else:
                self.buffer[y_pos].contents = self.buffer[y_pos].contents[:x_pos - 1] + char + self.buffer[y_pos].contents[:x_pos]

            return True

        except:
            return False


    #Deletes the character behind the cursor, returns "True" if no errors occurred. To delete the character at the end of the specified line
    #leave or set "x_pos" to "None".
    def delete_char(self, char: str, y_pos: int, x_pos: Optional[int] = None) -> bool:
        try:
            #If a line is empty we delete it.
            if (len(self.buffer[y_pos].contents)) == 0:
                self.buffer.pop(y_pos)
            #If we delete the first position of a line we simply append it to the line above, if there's one.
            elif x_pos == 0:
                if y_pos > 0:
                    self.buffer[y_pos - 1].contents += self.buffer[y_pos].contents
                    self.buffer.pop(y_pos)
            #If we want to delete the last character of the string we simply remove it using a string slice.
            elif x_pos == None:
                self.buffer[y_pos].contents = self.buffer[y_pos].contents[:len(self.buffer[y_pos].contents) - 2]
            else:
                self.buffer[y_pos].contents = self.buffer[y_pos].contents[:x_pos - 1] + self.buffer[y_pos].contents[:x_pos]

            return True

        except:
            return False


    def delete_char_forward(self, char: str, y_pos: int, x_pos: Optional[int] = None) -> bool:
        pass


    #Inserts a newline behind the cursor, returns "True" if no errors occurred. To insert it at the end of the specified line leave
    #or set "x_pos" to "None". Note that newline doesn't refer to the newline character "\n" but to what would happen when pressing
    #enter on a regular editor.
    def newline(self, y_pos: int, x_pos: Optional[int] = None) -> bool:
        try:
            #Insert a new line right after the current one.
            self.buffer.insert(y_pos + 1, Line())

            #If the current line isn't empty we slice it, leaving everything behind the cursor on it and putting everything in front of it in the
            #new line.
            if (len(self.buffer[y_pos].contents)) != 0:
                self.buffer[y_pos + 1].contents = self.buffer[y_pos].contents[x_pos:]
                self.buffer[y_pos].contents = self.buffer[y_pos].contents[:x_pos - 1]

            return True

        except:
            return False


    #Returns the character in the specified position if possible, otherwise returns "None".
    def get_char(self, y_pos: int, x_pos: int) -> Optional[str]:
        try:
            return self.buffer[y_pos].contents[x_pos + 1]

        except:
            return None


    #Returns the line in the specified position if possible, otherwise returns "None".
    def get_line(self, y_pos: int) -> Optional[str]:
        try:
            return self.buffer[y_pos].contents

        except:
            return None


    #Returns how many lines the buffer has, it's length.
    def get_line_count(self) -> int:
        return len(self.buffer)