import utils, curses, curses.ascii
from dataclasses import dataclass
from typing import Any

from buffer import TextBuffer
from cursor import Cursor


#This class contains configuration info pertaining to the buffer display. The Y and X ends are specified from the total height or width
#respectively. For example, a "y_end" of (-2) means that the Y size of the buffer will be the total height of the console window minus 2.
@dataclass
class BufferDisplayConfig:
    y_start: int = 0
    y_end: int = -2
    x_start: int = 0
    x_end: int = 0


class Display:
    #Any is used in the "editor" variable type to avoid circular referencing.
    def __init__(self, editor: Any, buffer: type[TextBuffer], cursor: type[Cursor]) -> None:
        self.editor = editor
        self.buffer = buffer
        self.cursor = cursor

        self.buffer_config = BufferDisplayConfig()


    #This function calls all the different display functions.
    def display(self) -> None:
        self.display_buffer()
        self.display_cursor()


    #Displays the buffer.
    def display_buffer(self) -> None:
        display_y = self.buffer_config.y_start
        end_y = self.editor.y_size + self.buffer_config.y_end
        end_x = self.editor.x_size + self.buffer_config.x_end

        #We iterate through every line and then every character. Every iteration we check if the printing indexes we are using have exceeded the
        #ones specified in the buffer configuration.
        for y in range(self.buffer.get_line_count()):
            display_x = self.buffer_config.x_start

            for char in self.buffer.get_line(y):
                self.editor.stdscr.addstr(display_y, display_x, char, self.editor.get_colour("WHITE_BLACK"))

                display_x += 1
                if display_x > end_x:
                    break

            display_y += 1
            if display_y > end_y:
                break


    #Displays the cursor
    def display_cursor(self) -> None:
        cursor_char = " "
        cursor_y = self.cursor.get_y()
        cursor_x = self.cursor.get_x()

        if cursor_x != len(self.buffer.get_line(cursor_y)) and len(self.buffer.get_line(cursor_y)) != 0:
            cursor_char = self.buffer.get_char(cursor_y, cursor_x)

        self.editor.stdscr.addstr(cursor_y, cursor_x, cursor_char, self.editor.get_colour("BLACK_WHITE"))