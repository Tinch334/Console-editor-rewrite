import utils, curses, curses.ascii

from buffer import TextBuffer
from cursor import Cursor
from display import Display

class TextEditor(utils.CursesUtils):
    def __init__(self):
        super().__init__()

        #####CONFIGURATION#####
        #Make "getch" non-blocking.
        self.stdscr.nodelay(True)

        #####GENERAL VARIABLES#####
        #Last pressed key.
        self.key = 0
        #The text buffer.
        self.buffer = TextBuffer()

        self.buffer.get_line_count()

        self.cursor = Cursor()
        self.display = Display(self, self.buffer, self.cursor)


    def text_editor(self) -> None:
        while 1:
            #Clear the screen
            self.stdscr.clear()
            

            #Get and process key input.
            self.get_input()

            #Call the display function.
            self.display.display()


            #####FOR TESTING#####
            if self.key == ord('q'):
                #Properly exit curses and exit the program.
                curses.endwin()
                quit()


            self.stdscr.addstr(5, 0, "Y: {} X: {}".format(self.cursor.get_y(), self.cursor.get_x()), self.get_colour("WHITE_BLACK"))


            #Get console size.
            self.get_size()
            #Refresh the screen.
            self.stdscr.refresh()
            #Gets the pressed key code.
            self.key = self.stdscr.getch()


    def get_input(self) -> None:
        if self.key == (-1):
            return

        if curses.ascii.isalnum(self.key) or curses.ascii.isblank(self.key):
            self.buffer.add_char(chr(self.key), self.cursor.get_y(), self.cursor.get_x())
            self.cursor.change_x_pos(True, self.buffer)


        elif curses.ascii.ctrl(self.key):
            self.buffer.delete_char(self.cursor.get_y(), self.cursor.get_x())
            self.cursor.change_x_pos(False, self.buffer)

        


editor = TextEditor()
editor.text_editor();