import curses, curses.ascii, os.path

from actions.utils import CursesUtils
from buffer.buffer import TextBuffer
from buffer.cursor import Cursor
from display.display import Display
from actions.input_output import IOHandler
from configuration.config import ConfigurationHandler
from actions.prompt import Prompt
from actions.command_help import CommandHelp
from actions.basic_input import BasicInput
from actions.find import FindInBuffer
from actions.undo import Undo


class TextEditor(CursesUtils):
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
        #The editor's configuration.
        self.editor_config = self.config.get_editor_config()

        #The text buffer handler.
        self.buffer = TextBuffer()
        #The cursor handler.
        self.cursor = Cursor(self.config.get_cursor_config())
        #The I/O handler.
        self.io = IOHandler()
        #The prompt handler.
        self.prompt = Prompt("COMMANDS: Ctrl+S - save | Ctrl+O - open | Ctrl+A - command help | Ctrl+Q - quit", self.editor_config.forget_time)
        #The display handler.
        self.display = Display(self, self.buffer, self.cursor, self.prompt, self.io, self.config.get_display_config(), self.config.get_display_colour_config())
        #Basic input handler.
        self.basic_input = BasicInput(self, self.config.get_display_colour_config())
        #Command help handler.
        self.command_help = CommandHelp(["Ctrl+G - goto line | Ctrl+W - word count | Ctrl+F - find", "Consectetur adipiscing elit. Nulla non neque rutrum lacus dapibus lobortis.", "Maecenas lobortis nibh massa, in varius leo auctor eget"], self.editor_config.forget_time)
        #Find in buffer.
        self.find_in_buffer = FindInBuffer(self.buffer)
        #Undo.
        self.undo_handler = Undo(0.5, 15)


    def text_editor(self) -> None:
        while True:
            #Clear the screen
            self.stdscr.clear()

            #Get and process key input.
            self.get_input()

            #Call the display function.
            self.display.display()

            #Call all handlers.
            self.prompt.prompt_handler()
            self.command_help.help_line_handler()
            self.undo_handler.undo_handler(self.buffer.get_buffer(), self.cursor.get_cursor_value())

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
            #Since we've modified the buffer we call the appropriate function.
            self.buffer_modified_handler()

        #Backspace
        elif key == curses.ascii.BS:
            #The reason we store the old cursor position is so we can modify the cursor, by calling "change_x_pos", before trying to delete a
            #character. We do this to solve a problem that would occur when deleting at the end of a line. What would occur is that the cursor
            #would get positioned at the end of the new line because "change_x_pos" uses the length of the line to get it's position.
            old_y = self.cursor.get_y()
            old_x = self.cursor.get_x()

            self.cursor.change_x_pos(False, self.buffer)
            self.buffer.delete_char(old_y, old_x)

            #Since we've modified the buffer we call the appropriate function.
            self.buffer_modified_handler()

        #Supr
        elif key == curses.KEY_DC:
            self.buffer.delete_char_forward(self.cursor.get_y(), self.cursor.get_x())
            #Since we've modified the buffer we call the appropriate function.
            self.buffer_modified_handler()

        #Enter, to detect it we use the ASCII "Carriage return(CR)" or "Line feed(LF)", both are included for compatibility reasons.
        elif key == curses.ascii.CR or key == curses.ascii.LF:
            self.buffer.newline(self.cursor.get_y(), self.cursor.get_x())
            #When the enter key is pressed we move the cursor down one line and then set it to the start of the line
            self.cursor.change_y_pos(1, self.buffer)
            #Set the cursor to the beginning of the new line.
            self.cursor.cursor_start()
            #Since we've modified the buffer we call the appropriate function.
            self.buffer_modified_handler()


        #Tab key.
        elif key == curses.ascii.TAB:
            tab_size = self.editor_config.tab_size
            cursor_x = self.cursor.get_x()

            tabs_to_insert = (tab_size - (cursor_x % tab_size))

            #Since there's no function in the buffer to insert a string we just add the space characters one by one, whilst moving the cursor
            #at the same time.
            for x in range(tabs_to_insert):
                self.buffer.add_char(" ", self.cursor.get_y(), self.cursor.get_x() + x)
                self.cursor.change_x_pos(True, self.buffer)

            #Since we've modified the buffer we call the appropriate function.
            self.buffer_modified_handler()

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

        #####"CTRL" keys#####
        #To detect keys pressed in conjunction with "Ctrl" we check for the uppercase ASCII value of the key minus 64, which is the value returned
        #when pressing a key plus "Ctrl". For example pressing CTRL+E would get a keycode of 5.
        #Ctrl+S -- Save
        elif key == ord("S") - 64:
            self.save_handler()

        #Ctrl+O -- Open
        elif key == ord("O") - 64:
            self.load_handler()

        #Ctrl+A -- Command help
        elif key == ord("A") - 64:
            self.prompt.change_prompt(self.command_help.get_help_line())

        #Ctrl+G -- Goto line.
        elif key == ord("G") - 64:
            self.goto_line()

        #Ctrl+W -- Word count
        elif key == ord("W") - 64:
            self.word_count()

        #Ctrl+Q -- Quit
        elif key == ord("Q") - 64:
            #Properly terminate curses and exit the program.
            curses.endwin()            
            quit()

        #Ctrl+F -- Find
        elif key == ord("F") - 64:
            self.find()

        #Ctrl+Z -- Undo
        elif key == ord("Z") - 64:
            self.undo()


    #To be called every time the buffer is modified.
    def buffer_modified_handler(self) -> None:
        #Set the dirty flag.
        self.io.set_dirty()
        #Set the display mode to normal.
        self.display.display_mode_handler.set_normal_display_mode()
        #Since the buffer has been modified we want to add these changes to the undo stack.
        self.undo_handler.set_undo()


    #Handles calling the I/O saving function and it's errors.
    def save_handler(self) -> None:
        filename = self.io.get_filename()

        #In case there's no specified filename we get one.
        if filename == None:
            #Disable the prompt, get input and then re-enable the prompt.
            self.prompt.toggle_enabled()
            filename = self.basic_input.basic_input(self.y_size - 1, 0, "Save file: ")
            self.prompt.toggle_enabled()

            #The escape key was pressed, therefore no filename was entered.
            if filename == None:
                return

        result = self.io.save_file(self.buffer, filename)

        #No errors occurred, display size of file saved in the prompt.
        if result > 0:
            self.prompt.change_prompt(f"{os.path.getsize(filename)} bytes written to disk")
        else:
            self.prompt.change_prompt(f"Failed to save file, make sure the location exists and you have permission")


    #Handles calling the I/O loading function and it's errors.
    def load_handler(self) -> None:
        #Disable the prompt, get input and then re-enable the prompt.
        self.prompt.toggle_enabled()
        filename = self.basic_input.basic_input(self.y_size - 1, 0, "Open file: ")
        self.prompt.toggle_enabled()

        #The escape key was pressed, therefore no filename was entered.
        if filename == None:
            return

        result = self.io.load_file(self.buffer, filename)

        #No errors occurred, display size of file opened in the prompt.
        if result > 0:
            self.prompt.change_prompt(f"Loaded {os.path.getsize(filename)} bytes from {filename}")
        else:
            self.prompt.change_prompt(f"Failed to open file, make sure the file exists and you have permission")


    #Gets a line number using basic input and then goes to it.
    def goto_line(self) -> None:
        #Disable the prompt, get input and then re-enable the prompt.
        self.prompt.toggle_enabled()
        line = self.basic_input.basic_input(self.y_size - 1, 0, "Line number: ")
        self.prompt.toggle_enabled()

        #The escape key was pressed, therefore no line was entered.
        if line == None:
            return

        #We make sure the user entered a number.
        try:
            line = int(line)

        except:
            #If an invalid value was entered show an error in the prompt and exit.
            self.prompt.change_prompt("Invalid line entered")
        else:
            #Check if the jump was successful, i.e. if the line exists.
            if self.cursor.change_y_pos((line - self.cursor.get_y() - 1), self.buffer):
                #Set the cursor to the beginning of the new line.
                self.cursor.cursor_start()
            else:
                self.prompt.change_prompt("Invalid line entered")


    #Counts the number of words in the file and displays it in the console.
    def word_count(self) -> None:
        words = 0

        #Counts all strings composed of alphanumeric characters separated by spaces in the buffer.
        for y in range(0, self.buffer.get_line_count()):
            for word in self.buffer.get_line(y).split():
                if (word.isalpha()):
                    words += 1

        self.prompt.change_prompt(f"There are {words} words in the current file")


    #Finds all the matches for the given regex, then highlights the matches.
    def find(self) -> None:
        #Disable the prompt, get input and then re-enable the prompt.
        self.prompt.toggle_enabled()
        regex_to_find = self.basic_input.basic_input(self.y_size - 1, 0, "Regex to find: ")
        self.prompt.toggle_enabled()

        #In case the user pressed "esc".
        if regex_to_find == None:
            return

        matches = self.find_in_buffer.find_in_buffer(regex_to_find)

        if matches != None:
            #Calculate the number of matches and display it.
            match_count = sum([len(a) for a in matches.values()])
            self.prompt.change_prompt(f"Found {match_count} matches for \"{regex_to_find}\"")

            #Set the display mode.
            self.display.display_mode_handler.set_highlight_display_mode(matches)

        else:
            self.prompt.change_prompt(f"No matches found for \"{regex_to_find}\"")


    #Reverts the editor to the last snapshot, undos the last actions.
    def undo(self) -> None:
        undo_result = self.undo_handler.get_undo()

        if undo_result == None:
            self.prompt.change_prompt("Nothing to undo")
        else:
            #Sets the buffer and cursor from the undo results.
            self.buffer.set_buffer(undo_result[0])
            self.cursor.set_cursor_value(undo_result[1])



editor = TextEditor()
editor.text_editor()