import curses
from typing import final


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

        #Gets filled with a reference to each possible colour pair.
        self.colours = {}
        #Fills "self.colours" with each possible colour pair.
        self.generate_colours()


    #Defines every possible colour pair(without attributes), and then relates their number with the corresponding name in the "self.colours"
    #dictionary. The naming convention is: Foreground colour first and then the background colour, with an underscore separating both colours.
    @final
    def generate_colours(self) -> None:
        #Colour variables.
        colour_reference = {"BLACK" : curses.COLOR_BLACK, "BLUE" : curses.COLOR_BLUE, "CYAN" : curses.COLOR_CYAN,
        "GREEN" : curses.COLOR_GREEN, "MAGENTA" : curses.COLOR_MAGENTA, "RED" : curses.COLOR_RED, "WHITE" : curses.COLOR_WHITE,
        "YELLOW" : curses.COLOR_YELLOW}

        colour_cont = 1

        for col_1 in colour_reference:
            for col_2 in colour_reference:
                #Create each colour's name.
                key = str(col_1) + "_" + str(col_2)

                curses.init_pair(colour_cont, colour_reference[col_1], colour_reference[col_2])
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


    #Prints a centred string at the specified height. If "fill" is True then both sides of the printed text will be filled with the character
    #in "fill_char", using the provided colour.
    @final
    def addctstr(self, y_pos: int, text: str, colour: int, fill: bool = False, fill_char: str = " ") -> None:
        #Shortens the text in case it's larger than the console.
        text = text[:self.x_size - 1]
        x_pos = int((self.x_size - len(text)) / 2)

        #Fill both sides of the printed text.
        if fill:
            self.stdscr.addstr(y_pos, 0, fill_char * self.x_size, colour)

        self.stdscr.addstr(y_pos, x_pos, text, colour)


    #Prints a centred multi-line title. The title has to be a list and all the lines have to have the same length. Otherwise the title won't
    #properly centre.
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