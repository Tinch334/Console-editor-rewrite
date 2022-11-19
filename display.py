import utils, math
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

    line_number_min_width = 2


#This class contains colour configuration for the various elements in the editor.
@dataclass
class BufferColourConfig:
    text_colour = "WHITE_BLACK"
    cursor_colour = "BLACK_WHITE"
    line_number_colour = "BLACK_WHITE"
    empty_line_colour = "WHITE_BLACK"


class Display:
    #Any is used in the "editor" variable type to avoid circular referencing.
    def __init__(self, editor: Any, buffer: type[TextBuffer], cursor: type[Cursor]) -> None:
        self.editor = editor
        self.buffer = buffer
        self.cursor = cursor

        #Configuration dataclasses for the display function.
        self.buffer_config = BufferDisplayConfig()
        self.colour_config = BufferColourConfig()

        #These two variables determine the scroll of the buffer. What this does is determine at which index the contents of the editor should
        #start being printed. For example a "buffer_y_scroll" of 5 means that the first 5 lines would not be displayed.
        self.buffer_y_scroll = 0
        self.buffer_x_scroll = 0


    #This function calls all the different display functions, it's the one that should be called from the editor.
    def display(self) -> None:
        #The line numbers are printed first because in the process of printing them their width is calculated, that value is then used to print
        #the buffer and cursor. We can call this function before calculating the scroll because we aren't printing the buffer, cursor or
        #anything related to scroll.
        self.display_line_nums()

        #Before printing anything we update the scroll variables.
        self.scroll_handler()

        self.display_buffer()
        self.display_cursor()

        #FOR TESTING
        self.editor.stdscr.addstr(self.editor.y_size + self.buffer_config.y_end, 0, "---------", self.editor.get_colour("WHITE_BLUE"))


    #Displays the buffer.
    def display_buffer(self) -> None:
        display_y = self.buffer_config.y_start

        end_y = self.editor.y_size + self.buffer_config.y_end
        end_x = self.editor.x_size + self.buffer_config.x_end

        #We iterate through every line between the scroll and the end of the buffer, we do the same in each line with the characters. Every
        #iteration we check if the printing indexes we are using have exceeded the ones specified in the buffer configuration to avoid printing
        #out of bounds.
        for y in range(self.buffer_y_scroll, self.buffer.get_line_count()):
            display_x = self.buffer_config.x_start
            current_line = self.buffer.get_line(y)

            for x in range(self.buffer_x_scroll, len(current_line)):
                self.editor.stdscr.addstr(display_y, display_x, current_line[x], self.editor.get_colour(self.colour_config.text_colour))
    
                #X printing index check.
                display_x += 1
                if display_x >= end_x:
                    break

            #Y printing index check.
            display_y += 1
            if display_y > end_y:
                break


    #Displays line numbers an calculates "buffer_config.x_start".
    def display_line_nums(self) -> None:
        #The number of characters required to display the maximum number of lines.
        line_number_width = max(int(math.log10(self.buffer.get_line_count())) + 1, self.buffer_config.line_number_min_width)
        #We set the x_start according to the width of the line number.
        self.buffer_config.x_start = line_number_width

        end_y = self.editor.y_size + self.buffer_config.y_end

        for y in range(self.buffer_config.y_start, end_y):
            #In case we are at the very end of the buffer, and there's empty space before the status-bar.
            if y + self.buffer_y_scroll < self.buffer.get_line_count():
                num_width = int(math.log10(y + 1)) + 1
                padding = " " * (line_number_width - num_width - self.buffer_y_scroll)
                #To calculate the current line number we add the buffer scroll to the y counter, that way it remains correct even when the
                #buffer is scrolled vertically. Finally we add 1 to account for the fact that line numbers start at 1, not 0.
                line_number = y + self.buffer_y_scroll + 1

                self.editor.stdscr.addstr(y, 0, f"{padding}{line_number}", self.editor.get_colour(self.colour_config.line_number_colour))
            else:
                self.editor.stdscr.addstr(y, 0, "~", self.editor.get_colour(self.colour_config.empty_line_colour))


    #Displays the cursor
    def display_cursor(self) -> None:
        cursor_char = " "
        cursor_y = self.cursor.get_y()
        cursor_x = self.cursor.get_x()

        #If there's a character under the cursor we have to print it under it.
        if cursor_x != len(self.buffer.get_line(cursor_y)) and len(self.buffer.get_line(cursor_y)) != 0:
            cursor_char = self.buffer.get_char(cursor_y, cursor_x)

        #When calculating the position of the cursor we must consider the current scroll of the buffer.
        self.editor.stdscr.addstr(cursor_y - self.buffer_y_scroll, cursor_x + self.buffer_config.x_start - self.buffer_x_scroll, cursor_char, self.editor.get_colour(self.colour_config.cursor_colour))


    #Handles the horizontal and vertical scroll for printing the appropriate part of the buffer depending on the position of the cursor. 
    def scroll_handler(self) -> None:        
        end_y = self.editor.y_size + self.buffer_config.y_end
        end_x = self.editor.x_size + self.buffer_config.x_end
        cursor_y = self.cursor.get_y()
        cursor_x = self.cursor.get_x()

        #First we check if the cursor has gone beneath the printed part of the buffer. For this we check the Y position of the cursor against
        #the final size of the printed buffer, "end_y", added to the current Y scroll minus 1, to account for the index. In case it's true we
        #set the scroll to be enough so the cursor appears on the last line.
        if cursor_y > end_y + self.buffer_y_scroll - 1:
            self.buffer_y_scroll = cursor_y - end_y + 1
        #If the cursor goes above the printed part of the buffer we set the scroll to the cursor's position, which is just enough for the cursor
        #to appear on the first line.
        elif cursor_y < self.buffer_y_scroll:
            self.buffer_y_scroll = cursor_y

        #Same concept except in the X axis, except that we also take into account the fact that "start_x" can be not zero, when the line
        #numbers are enabled.
        if cursor_x > end_x - self.buffer_config.x_start + self.buffer_x_scroll - 1:
            self.buffer_x_scroll = cursor_x - end_x + self.buffer_config.x_start + 1 
        #If the cursor goes above the printed part of the buffer we set the scroll to the cursor's position, which is just enough for the cursor
        #to appear on the first line.
        elif cursor_x < self.buffer_x_scroll:
            self.buffer_x_scroll = cursor_x