import curses
from typing import Any, Optional

from actions.config import DisplayColourConfig


#Allows for basic singe line input. Returns the entered string or "None" if the escape key was pressed.
class BasicInput():
    def __init__(self, editor: Any, colour_config: type[DisplayColourConfig]) -> None:
        #####ARGUMENTS#####
        #A reference to the editor class. This is so that the basic loop functions can still be called whilst using the input.
        self.editor = editor

        #####COLOUR#####
        self.colour_config = colour_config
        #The text_colour for the prompt and entered text.

        #####CLASS VARIABLES#####
        #The entered text.
        self.text = ""
        #The cursor position in the entered text,
        self.cursor_pos = 0


    def basic_input(self, y_pos: int, x_pos: int, prompt: str) -> None:
        #Reset input variables.
        self.text = ""
        self.cursor_pos = 0

        while True:
            #Clear the screen
            self.editor.stdscr.clear()

            #Detect keys that modify the entered string.
            self.detect_key()
            #Detect the keys that can cause the program to return.
            returned_value = self.detect_return_key()
            #We now check to make sure we aren't returning an empty string directly.
            if returned_value != "":
                return returned_value

            #Call the display function.
            self.editor.display.display()
            #Call the input's display function.
            self.display_input(y_pos, x_pos, prompt)

            #Get console size.
            self.editor.get_size()
            #Refresh the screen.
            self.editor.stdscr.refresh()
            #Gets the pressed key code.
            self.editor.key = self.editor.stdscr.getch()


    #Keys that cause the program to return.
    def detect_return_key(self) -> Optional[str]:
        #We use the "key" variable to avoid accessing the class variable repeated times.
        key = self.editor.key

        #Enter key was pressed, we return the entered text.
        if key == curses.ascii.CR or key == curses.ascii.LF:
            return self.text

        #Escape key was pressed, we return nothing.
        elif key == 27:
            return None

        else:
            #In case no return key was detected we return an empty string, to avoid returning.
            return ""


    #Input key detection.
    def detect_key(self) -> None:
        #We use the "key" variable to avoid accessing the class variable repeated times.
        key = self.editor.key

        #Printable ASCII characters
        if key >= 32 and key <= 253:
            #Insert the given char at the current cursor position. Since python strings are immutable we create a new string
            #consisting of the previous string split where the cursor is plus the added character.
            text_before = self.text[:self.cursor_pos]
            text_after = self.text[self.cursor_pos:]
            self.text = text_before + chr(key) + text_after

            #Move the cursor's position.
            self.cursor_pos += 1

        #Backspace
        elif key == 8:
            #If the line isn't empty delete the corresponding character.
            if self.cursor_pos > 0:
                #Copy all the text in the current line except the char to the left of the cursor.
                self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1

        elif key == curses.KEY_LEFT:
            #Move the cursor.
            if self.cursor_pos > 0:
                self.cursor_pos -= 1

        elif key == curses.KEY_RIGHT:
            #Move the cursor.
            if self.cursor_pos < len(self.text):
                self.cursor_pos += 1

        #Start key.
        elif key == curses.KEY_HOME:
            self.cursor_pos = 0

        #End key.
        elif key == curses.KEY_END:
            self.cursor_pos = len(self.text)


    #Displays the basic input line.
    def display_input(self, y_pos, x_pos, prompt) -> None:
        #Print the prompt, entered text and escape key reminder.
        self.editor.stdscr.addstr(y_pos, x_pos, f"{prompt}{self.text}  (ESC to cancel)", self.editor.get_colour(self.colour_config.text_colour))

        #Print the cursor, detecting if it's in the last char and reacting accordingly.
        if self.cursor_pos == len(self.text):
            self.editor.stdscr.addstr(y_pos, self.cursor_pos + len(prompt), " ", self.editor.get_colour(self.colour_config.cursor_colour))
        else:
            self.editor.stdscr.addstr(y_pos, self.cursor_pos + len(prompt), self.text[self.cursor_pos], self.editor.get_colour(self.colour_config.cursor_colour))