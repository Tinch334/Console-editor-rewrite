import utils, curses, curses.ascii

from buffer import TextBuffer
from cursor import Cursor
from display import Display
from input_output import IOHandler
from config import ConfigurationHandler


class TextEditor(utils.CursesUtils):
    def __init__(self):
        super().__init__()

        #####CONFIGURATION#####
        #Make "getch" non-blocking.
        self.stdscr.nodelay(True)

        #####GENERAL VARIABLES#####
        #Last pressed key.
        self.key = 0

        #####CLASSES#####
        #The configuration handler.
        self.config = ConfigurationHandler()
        #The text buffer handler.
        self.buffer = TextBuffer()
        #The cursor handler.
        self.cursor = Cursor(self.config.get_cursor_config())
        #The I/O handler.
        self.io = IOHandler()
        #The display handler.
        self.display = Display(self, self.buffer, self.cursor, self.io, self.config.get_display_config(), self.config.get_display_colour_config())


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

            #Get console size.
            self.get_size()
            #Refresh the screen.
            self.stdscr.refresh()
            #Gets the pressed key code.
            self.key = self.stdscr.getch()


    def get_input(self) -> None:
        #We use the "key" variable to avoid accessing the class variable repeated times.
        key = self.key

        #In non-blocking mode the function "getch" returns "(-1)" when no key was pressed.
        if key == (-1):
            return

        #####Input keys#####
        #Printable characters, this range covers all of extended ASCII, including symbols.
        if key >= 32 and key <= 253:
            self.buffer.add_char(chr(key), self.cursor.get_y(), self.cursor.get_x())
            self.cursor.change_x_pos(True, self.buffer)
            #Since we've modified the buffer we set the dirty flag.
            self.io.set_dirty()

        #Backspace
        elif key == curses.ascii.BS:
            #The reason we store the old cursor position is so we can modify the cursor, by calling "change_x_pos", before trying to delete a
            #character. We do this to solve a problem that would occur when deleting at the end of a line. What would occur is that the cursor
            #would get positioned at the end of the new line because "change_x_pos" uses the length of the line to get it's position.
            old_y = self.cursor.get_y()
            old_x = self.cursor.get_x()

            self.cursor.change_x_pos(False, self.buffer)
            self.buffer.delete_char(old_y, old_x)

            #Since we've modified the buffer we set the dirty flag.
            self.io.set_dirty()

        #Supr
        elif key == curses.KEY_DC:
            self.buffer.delete_char_forward(self.cursor.get_y(), self.cursor.get_x())
            #Since we've modified the buffer we set the dirty flag.
            self.io.set_dirty()

        #Enter, to detect it we use the ASCII "Carriage return(CR)" or "Line feed(LF)", both are included for compatibility reasons.
        elif key == curses.ascii.CR or key == curses.ascii.LF:
            self.buffer.newline(self.cursor.get_y(), self.cursor.get_x())
            #When the enter key is pressed we move the cursor down one line and then set it to the start of the line
            self.cursor.change_y_pos(1, self.buffer)
            self.cursor.cursor_start()
            #Since we've modified the buffer we set the dirty flag.
            self.io.set_dirty()

        #####Cursor movement keys#####
        elif key == curses.KEY_RIGHT:
            self.cursor.change_x_pos(True, self.buffer)

        elif key == curses.KEY_LEFT:
            self.cursor.change_x_pos(False, self.buffer)

        elif key == curses.KEY_UP:
            self.cursor.change_y_pos(-1, self.buffer)

        elif key == curses.KEY_DOWN:
            self.cursor.change_y_pos(1, self.buffer)

        elif key == curses.KEY_HOME:
            self.cursor.cursor_start()

        elif key == curses.KEY_END:
            self.cursor.cursor_end(self.buffer)

        elif key == curses.KEY_PPAGE:
            self.cursor.cursor_scroll(True, self.buffer)

        elif key == curses.KEY_NPAGE:
            self.cursor.cursor_scroll(False, self.buffer)
            


editor = TextEditor()
editor.text_editor();