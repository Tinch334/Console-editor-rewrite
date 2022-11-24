import datetime

from buffer.buffer import TextBuffer
from buffer.cursor import Cursor
from actions.input_output import IOHandler


#The status-bar functions are in another class to avoid cluttering the "Display" class with too many functions.
class StatusbarFunctions:
    def __init__(self, buffer: type[TextBuffer], cursor: type[Cursor], io: type[IOHandler]) -> None:
            self.buffer = buffer
            self.cursor = cursor
            self.io = io


    #Returns the name of the current filename.
    def statusbar_filename(self) -> str:
        filename = self.io.get_filename()
        return (filename if filename != None else "[No filename]")


    #Returns the number of lines in the current buffer.
    def statusbar_lines(self) -> str:
        lines = self.buffer.get_line_count()
        s_str = ("" if lines == 1 else "s")
        return f"{lines} line{s_str}"


    #Returns whether or not the buffer has been modified since it was saved.
    def statusbar_modified(self) -> str:
        return ("(modified)" if self.io.get_dirty() else "")


    #Returns the current time in 24 hour format.
    def statusbar_time(self) -> str:
        current_time = datetime.datetime.now()
        return "{:02d}:{:02d}".format(current_time.hour, current_time.minute)


    #Returns the position of the cursor, first vertical the horizontal. We add 1 to both so they start counting from one.
    def statusbar_cursor(self) -> str:
        return f"{self.cursor.get_y() + 1},{self.cursor.get_x() + 1}"