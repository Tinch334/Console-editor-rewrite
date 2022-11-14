import curses
from typing import final, Union, Callable, Iterable, Any, Type



#A class with functions to use with the curses library, the class that wishes to use the functions must inherit from this one.
class CursesUtils():
    def __init__(self) -> None:
        self.stdscr = curses.initscr()

        #Configure the console
        curses.noecho()
        curses.raw()
        curses.curs_set(0)
        curses.start_color()
        self.stdscr.keypad(True)

        #Clear and refresh the screen for a blank canvas.
        self.stdscr.clear()
        self.stdscr.refresh()

        #Initialize console size variables.
        self.y_size = 0
        self.x_size = 0
        self.get_size()

        #Key detection variables.
        self.key = 0

        #Colour variables.
        self.colour_reference = {"BLACK" : curses.COLOR_BLACK, "BLUE" : curses.COLOR_BLUE, "CYAN" : curses.COLOR_CYAN,
        "GREEN" : curses.COLOR_GREEN, "MAGENTA" : curses.COLOR_MAGENTA, "RED" : curses.COLOR_RED, "WHITE" : curses.COLOR_WHITE,
        "YELLOW" : curses.COLOR_YELLOW}
        #Gets filled with a reference to each possible colour pair.
        self.colours = {}

        self.generate_colours()


    #Defines every possible colour pair(without attributes), and then relates their number with the corresponding name in the
    #"self.colours" dictionary. The naming convention is: Foreground colour first and then the background colour, with an
    #underscore separating both colours.
    @final
    def generate_colours(self) -> None:
        colour_cont = 1

        for col_1 in self.colour_reference:
            for col_2 in self.colour_reference:
                #Create each colour's name.
                key = str(col_1) + "_" + str(col_2)

                curses.init_pair(colour_cont, self.colour_reference[col_1], self.colour_reference[col_2])
                self.colours[key] = colour_cont

                colour_cont += 1


    #Simplifies using the colour dictionary. Allows the user to use "self.get_colour(colour)" instead of 
    #"curses.color_pair(self.colours[colour])" to select a colour pair.
    @final
    def get_colour(self, colour: str) -> int:
        try:
            return curses.color_pair(self.colours[colour])
        except:
            #(-1) is the default value for a white foreground and black background.
            return curses.color_pair(-1)


    #Gets the console size.
    @final
    def get_size(self) -> None:
        self.y_size, self.x_size = self.stdscr.getmaxyx()


    #Prints a centred string at the specified height. If "fill" is True then both sides of the printed text will be filled with
    #the character in "fill_char", using the provided colour.
    @final
    def addctstr(self, y_pos: int, text: str, colour: int, fill: bool = False, fill_char: str = " ") -> None:
        #Shortens the text in case it's larger than the console.
        text = text[:self.x_size - 1]
        x_pos = int((self.x_size - len(text)) / 2)

        #Fill both sides of the printed text.
        if fill:
            self.stdscr.addstr(y_pos, 0, fill_char * self.x_size, colour)

        self.stdscr.addstr(y_pos, x_pos, text, colour)


    #Prints a centred multi-line title. The title has to be a list and all the lines have to have the same length. Otherwise
    #the title won't properly centre.
    @final
    def print_title(self, title: str, hight: int, colour: int) -> None:
        if isinstance(title, list) and hight >= 0:
            for a in range(len(title)):
                self.addctstr(hight + a, title[a], colour)


    #Exactly the same as "addstr" but can print in the lowermost right corner of the console.
    @final
    def addstrex(self, y_pos: int, x_pos: int, string: str, colour: int) -> None:
        #Catch the exception caused by printing in the lower right corner of the console.
        try:
            self.stdscr.addstr(y_pos, x_pos, string, colour)
        except curses.error:
            pass



#Allows for basic singe line input. Returns the entered string. Still requires the program loop to function. As a note, what
#this type hint "class_ref: Type[CursesUtils] = CursesUtils", means that "class_ref" should be of type CursesUtils or one of
#it's descendants.
class BasicInput():
    def __init__(self, class_ref: Type[CursesUtils], y_pos: int, x_pos: int, prompt: str, colour: int, cursor_colour: int, cursor_colour_over_text: int) -> None:
        #####ARGUMENTS#####
        #A reference to the class that called the function.
        self.class_ref = class_ref
        #Position of the prompt in the y axis.
        self.y_pos = y_pos
        #Position of the prompt in the x axis.
        self.x_pos = x_pos
        #Prompt before the text
        self.prompt = prompt
        #The colour for the prompt and entered text.
        self.colour = colour
        #The colour of the cursor.
        self.cursor_colour = cursor_colour
        self.cursor_colour_over_text = cursor_colour_over_text

        #####CLASS VARIABLES#####
        self.text = ""
        self.cursor_pos = 0


    def basic_input(self) -> None:
        while True:
            self.class_ref.stdscr.clear()
            self.class_ref.get_size()

            self.detect_key()
            #Detect the keys that can cause the program to return. Minus one is used as the default value because the class
            #needs to be able to return "None".
            returned_value = self.detect_return_key()
            if returned_value != (-1):
                return returned_value

            self.display()
            self.class_ref.print_screen()

            self.class_ref.stdscr.refresh()
            self.class_ref.key = self.class_ref.stdscr.getch()


    #Keys that cause the program to return.
    def detect_return_key(self) -> int:
        #Enter key. If pressed returns the entered text.
        if self.class_ref.key == 10 or self.class_ref.key == 13 or self.class_ref.key == curses.KEY_ENTER:
            if self.text != "":
                return self.text

        #Escape key.
        elif self.class_ref.key == 27:
            return None

        #An unexpected error occurred, return appropriately.
        return -1


    def detect_key(self) -> None:
        if self.class_ref.key >= 32 and self.class_ref.key <= 253:
            #Insert the given char at the current cursor position. Since python strings are immutable we create a new string
            #consisting of the previous string split where the cursor is plus the added character.
            text_before = self.text[:self.cursor_pos]
            text_after = self.text[self.cursor_pos:]
            self.text = text_before + chr(self.class_ref.key) + text_after

            #Move the cursor's position.
            self.cursor_pos += 1

        #Backspace
        elif self.class_ref.key == 8:
            #If the line isn't empty delete the corresponding character.
            if self.cursor_pos > 0:
                #Copy all the text in the current line except the char to the left of the cursor.
                self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1

        elif self.class_ref.key == curses.KEY_LEFT:
            #Move the cursor.
            if self.cursor_pos > 0:
                self.cursor_pos -= 1

        elif self.class_ref.key == curses.KEY_RIGHT:
            #Move the cursor.
            if self.cursor_pos < len(self.text):
                self.cursor_pos += 1

        #Start key.
        elif self.class_ref.key == curses.KEY_HOME:
            self.cursor_pos = 0

        #End key.
        elif self.class_ref.key == curses.KEY_END:
            self.cursor_pos = len(self.text)


    def display(self) -> None:
        #Print the prompt and entered text.
        self.class_ref.stdscr.addstr(self.y_pos, self.x_pos, self.prompt + self.text, self.colour)
        #Print the escape key reminder.
        self.class_ref.stdscr.addstr(self.y_pos, self.x_pos + len(self.prompt) + len(self.text) + 2, "(ESC to cancel)", self.colour)

        #Print the cursor. Detect if you are in the last char and react accordingly.
        if self.cursor_pos == len(self.text):
            self.class_ref.stdscr.addstr(self.y_pos, self.cursor_pos + len(self.prompt), " ", self.cursor_colour)
        else:
            self.class_ref.stdscr.addstr(self.y_pos, self.cursor_pos + len(self.prompt), self.text[self.cursor_pos], self.cursor_colour_over_text)