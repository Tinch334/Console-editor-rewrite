import utils, curses, curses.ascii
from buffer import TextBuffer
from cursor import Cursor


class TextEditor(utils.CursesUtils):
    def __init__(self):
        #####CONFIGURATION#####
        #Make "getch" non-blocking.
        self.stdscr.nodelay(True)

        #####GENERAL VARIABLES#####
        #Last pressed key.
        self.key = 0
        #The text buffer.
        self.buffer = TextBuffer()
        self.cursor = Cursor()


    def text_editor(self):
        while 1:
            #Clear the screen
            self.stdscr.clear()

            self.get_input()

            #Refresh the screen.
            self.stdscr.refresh()
            #Gets the pressed key code.
            self.key = stdscr.getch()



    def get_input(self):
        if curses.ascii.isalpha(self.key):
            self.buffer.add_char(ord(self.key), self.cursor.get_y())
            self.cursor.change_x_pos(True, self.buffer)

        


editor = TextEditor()
editor.text_editor();