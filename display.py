import math, re
from dataclasses import dataclass
from typing import Any

from buffer import TextBuffer
from cursor import Cursor
from input_output import IOHandler
from status_bar_functions import StatusbarFunctions


#This class contains configuration info pertaining to the buffer display. The Y and X ends are specified from the total height or width
#respectively. For example, a "y_end" of (-2) means that the Y size of the buffer will be the total height of the console window minus 2.
@dataclass
class BufferDisplayConfig:
    y_start: int = 0
    y_end: int = -2
    x_start: int = 0
    x_end: int = 0

    line_number_min_width = 2
    status_bar_config= r"filename-lines\modified/time-cursor"


#This class contains colour configuration for the various elements in the editor.
@dataclass
class BufferColourConfig:
    text_colour = "WHITE_BLACK"
    cursor_colour = "BLACK_WHITE"
    line_number_colour = "BLACK_WHITE"
    empty_line_number_colour = "WHITE_BLACK"
    status_bar_colour = "WHITE_BLUE"
    prompt_colour = "WHITE_BLACK"


class Display:
    #Any is used in the "editor" variable type to avoid circular referencing.
    def __init__(self, editor: Any, buffer: type[TextBuffer], cursor: type[Cursor], io: type[IOHandler]) -> None:
        self.editor = editor
        self.buffer = buffer
        self.cursor = cursor
        self.io = io

        #Configuration dataclasses for the display function.
        self.buffer_config = BufferDisplayConfig()
        self.colour_config = BufferColourConfig()
        #This class contains all the functions for the status-bar.
        self.status_bar_functions = StatusbarFunctions(self.buffer, self.cursor, self.io)

        #These two variables determine the scroll of the buffer. What this does is determine at which index the contents of the editor should
        #start being printed. For example a "buffer_y_scroll" of 5 means that the first 5 lines would not be displayed.
        self.buffer_y_scroll = 0
        self.buffer_x_scroll = 0

        #The reason for these to be class variables instead of just function variables is so that they are only calculated once, not every call
        #to the "display" function.
        self.status_bar_elements = None
        self.status_bar_separators = None

        #We call this function only once, during the constructor since the data we get from it won't change during runtime.
        self.setup()


    #Gets the value of variables that won't change during runtime.
    def setup(self) -> None:
        self.status_bar_elements = re.split(r"[-\\\/]", self.buffer_config.status_bar_config)
        self.status_bar_separators = re.findall(r"[-\\\/]", self.buffer_config.status_bar_config)


    #This function calls all the different display functions, it's the one that should be called from the editor.
    def display(self) -> None:
        #We calculate the x start of the buffer, for now equal to the line number width, that value is then used to print the buffer and
        #cursor. We can call this function before calculating the scroll because the scroll calculation uses the x start.
        self.caclculate_x_start()
        #Before printing anything we update the scroll variables.
        self.scroll_handler()

        self.display_buffer()
        self.display_cursor()
        self.display_line_nums()
        self.display_statusbar()


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
        end_y = self.editor.y_size + self.buffer_config.y_end

        for y in range(self.buffer_config.y_start, end_y):
            #In case we are at the very end of the buffer, and there's empty space before the status-bar.
            if y + self.buffer_y_scroll < self.buffer.get_line_count():
                num_width = int(math.log10(y + 1)) + 1
                padding = " " * (self.buffer_config.x_start - num_width - self.buffer_y_scroll)
                #To calculate the current line number we add the buffer scroll to the y counter, that way it remains correct even when the
                #buffer is scrolled vertically. Finally we add 1 to account for the fact that line numbers start at 1, not 0.
                line_number = y + self.buffer_y_scroll + 1

                self.editor.stdscr.addstr(y, 0, f"{padding}{line_number}", self.editor.get_colour(self.colour_config.line_number_colour))
            else:
                self.editor.stdscr.addstr(y, 0, "~", self.editor.get_colour(self.colour_config.empty_line_number_colour))


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


    #Assembles and displays the status-bar.
    def display_statusbar(self) -> None:
        statusbar_left = ""
        statusbar_right = ""
        contents = ""
        switch = False
        separator_index = 0

        #This dictionary contains the name of the element in the configuration as keys and the function that gets that information as elements.
        element_definitions = {"filename" : self.status_bar_functions.statusbar_filename(), "lines" : self.status_bar_functions.statusbar_lines(), "modified" : self.status_bar_functions.statusbar_modified(), "time" : self.status_bar_functions.statusbar_time(), "cursor" : self.status_bar_functions.statusbar_cursor()}

        #We go through every element in the configuration.
        for elem in self.status_bar_elements:
            #This check is done because after the last element there's no separator, however we still need to get to the end of this iteration
            #to print it the element in question.
            if separator_index < len(self.status_bar_separators):
                #We evaluate the separator.
                match self.status_bar_separators[separator_index]:
                    case "-":
                        contents = " - "

                    case "\\":
                        contents = " "

                    case "/":
                        switch = True
            else:
                contents = ""

            #This try block is here in case someone entered an invalid status-bar element.
            try:
                #We use the "switch" variable to determine if we should add elements to the left or right of the status-bar.
                if switch:
                    statusbar_right += element_definitions[elem]
                    statusbar_right += contents
                else:
                    statusbar_left += element_definitions[elem]
                    statusbar_left += contents
            except:
                raise Exception(f"Invalid status-bar element \"{elem}\"!")

            separator_index += 1

        #We add one space of right padding to the right side of the status-bar to make it look better.
        statusbar_right += " "
        #We put both sides of the status-bar together padding the space in the middle with spaces.
        assembled_statusbar = statusbar_left + " " * (self.editor.x_size - len(statusbar_left) - len(statusbar_right)) + statusbar_right

        #We print the status-bar.
        self.editor.stdscr.addstr(self.editor.y_size + self.buffer_config.y_end, 0, assembled_statusbar, self.editor.get_colour(self.colour_config.status_bar_colour))        


    def caclculate_x_start(self) -> None:
        #The number of characters required to display the maximum number of lines.
        line_number_width = max(int(math.log10(self.buffer.get_line_count())) + 1, self.buffer_config.line_number_min_width)
        #We set the x_start according to the width of the line number.
        self.buffer_config.x_start = line_number_width


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