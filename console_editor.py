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
        #We use the "key" variable to avoid accessing the class variable repeated times.
        key = self.key

        #The function "getch" returns "(-1)" when no key was pressed.
        if key == (-1):
            return

        #####Input keys#####
        if curses.ascii.isalnum(key) or curses.ascii.isblank(key):
            self.buffer.add_char(chr(key), self.cursor.get_y(), self.cursor.get_x())
            self.cursor.change_x_pos(True, self.buffer)

        #Backspace
        elif key == 8:
            self.buffer.delete_char(self.cursor.get_y(), self.cursor.get_x())
            self.cursor.change_x_pos(False, self.buffer)

        #Enter
        elif key == 10 or key == 13 or key == curses.KEY_ENTER:
            self.buffer.newline(self.cursor.get_y(), self.cursor.get_x())
            #When the enter key is pressed we move the cursor down one line and then set it to the start of the line
            self.cursor.change_y_pos(1, self.buffer)
            self.cursor.cursor_start()

        #####Cursor movement keys#####
        elif key == curses.KEY_RIGHT:
            self.cursor.change_x_pos(True, self.buffer)

        elif key == curses.KEY_LEFT:
            self.cursor.change_x_pos(False, self.buffer)

        elif key == curses.KEY_UP:
            self.cursor.change_y_pos(-1, self.buffer)

        elif key == curses.KEY_DOWN:
            self.cursor.change_y_pos(1, self.buffer)


editor = TextEditor()
editor.text_editor();