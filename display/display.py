import math, re
from dataclasses import dataclass
from typing import Any

from buffer.buffer import TextBuffer
from buffer.cursor import Cursor
from actions.input_output import IOHandler
from display.status_bar_functions import StatusbarFunctions
from actions.config import DisplayConfig, DisplayColourConfig


class Display:
    #Any is used in the "editor" variable type to avoid circular referencing.
    def __init__(self, editor: Any, buffer: type[TextBuffer], cursor: type[Cursor], io: type[IOHandler], buffer_config: type[DisplayConfig], colour_config: type[DisplayColourConfig]) -> None:
        self.editor = editor
        self.buffer = buffer
        self.cursor = cursor
        self.io = io

        #Configuration dataclasses for the display function.
        self.buffer_config = buffer_config
        self.colour_config = colour_config
        #This class contains all the functions for the status-bar.
        self.status_bar_functions = StatusbarFunctions(self.buffer, self.cursor, self.io)

        #These two variables determine the scroll of the buffer. What this does is determine at which index the contents of the editor should
        #start being printed. For example a "buffer_y_scroll" of 5 means that the first 5 lines would not be displayed.
        self.buffer_y_scroll = 0
        self.buffer_x_scroll = 0

        #The reason for these to be class variables instead of just function variables is so that they are only calculated once, not every call
        #to the "display" function.
        self.statusbar_elements = None
        self.statusbar_separators = None

        #We call this function only once, during the constructor since the data we get from it won't change during runtime.
        self.setup()


    #Gets the value of variables that won't change during runtime.
    def setup(self) -> None:
        self.statusbar_elements = re.split(r"[-\\\/]", self.buffer_config.statusbar_config)
        self.statusbar_separators = re.findall(r"[-\\\/]", self.buffer_config.statusbar_config)


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
                #To calculate the current line number we add the buffer scroll to the y counter, that way it remains correct even when the
                #buffer is scrolled vertically. Finally we add 1 to account for the fact that line numbers start at 1, not 0.
                line_number = y + self.buffer_y_scroll + 1
                num_width = int(math.log10(line_number)) + 1
                padding = " " * (self.buffer_config.x_start - num_width)

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
        separator = ""
        separator_index = 0
        switch = False

        #This dictionary contains the name of the element in the configuration as keys and the function that gets that information as elements.
        element_definitions = {"filename" : self.status_bar_functions.statusbar_filename(), "lines" : self.status_bar_functions.statusbar_lines(), "modified" : self.status_bar_functions.statusbar_modified(), "time" : self.status_bar_functions.statusbar_time(), "cursor" : self.status_bar_functions.statusbar_cursor()}

        #We go through every element in the configuration.
        for elem in self.statusbar_elements:
            #We use the "switch" variable to determine if we should add elements to the left or right of the status-bar.
            if switch:
                statusbar_right += element_definitions[elem]
            else:
                statusbar_left += element_definitions[elem]

            #This check is done because after the last element there's no separator, therefore we would be trying to access an invalid index.
            if separator_index >= len(self.statusbar_separators):
                break

            #We get the corresponding value for the separator.
            separator = self.buffer_config.statusbar_separators_definitions[self.statusbar_separators[separator_index]]

            #If the value is "(-1)" that means to switch from left to right.
            if separator == (-1):
                separator = ""
                switch = True

            #We use the "switch" variable to determine if we should add elements to the left or right of the status-bar.
            if switch:
                statusbar_right += separator
            else:
                statusbar_left += separator

            separator_index += 1

        #We add one space of right padding to the right side of the status-bar to make it look better.
        statusbar_right += " "
        #We put both sides of the status-bar together padding the space in the middle with spaces.
        separating_spaces = " " * (self.editor.x_size - len(statusbar_left) - len(statusbar_right))
        assembled_statusbar = f"{statusbar_left}{separating_spaces}{statusbar_right}"

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