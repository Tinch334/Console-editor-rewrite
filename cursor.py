from dataclasses import dataclass

from buffer import TextBuffer


@dataclass
class Cursor:
    y_pos: int = 0
    x_pos: int = 0

    #This variables stores the X position the cursor would like to be in, it's used when moving vertically from one line to another line and
    #the line we are moving to isn't long enough for the cursor to have it's previous horizontal position.
    #When not in use it's set to "-1" to allow for easy and always false comparisons using "max".
    _desired_x_pos = -1


    def get_y(self) -> int:
        return self.y_pos


    def get_x(self) -> int:
        return self.x_pos


    #Changes the X position of the cursor, if "change" is "True" then the cursor is moved one position to the right, otherwise it's moved one
    #position to the left.
    def change_x_pos(self, change: bool, buffer: type[TextBuffer]) -> None:
        new_pos = self.x_pos + (1 if change else -1)

        #First we check that the line we are trying to check exists, this is to deal with the case where we delete the last line. Then we check
        #that the cursor doesn't get to either end of the line.
        if buffer.get_line(self.y_pos) != None and new_pos < len(buffer.get_line(self.y_pos)) + 1 and new_pos >= 0:
            self.x_pos = new_pos
            #Otherwise we check to see if we can move the cursor vertically to the next/previous line accordingly.
        else:
            if change:
                if self.y_pos + 1 < buffer.get_line_count():
                    self.y_pos += 1
                    self.x_pos = 0
            else:
                if self.y_pos - 1 >= 0:
                    self.y_pos -= 1
                    self.x_pos = len(buffer.get_line(self.y_pos))


    #Changes the Y position of the cursor, the "change" can be both positive or negative. A reference to the buffer is required for the function
    #to work. Returns "True" if no errors occurred.
    def change_y_pos(self, change: int, buffer: type[TextBuffer]) -> bool:
        new_pos = self.y_pos + change

        #Make sure the cursor is being moved to a valid location.
        if new_pos < buffer.get_line_count() and new_pos >= 0:
            max_x = max(self.x_pos, self._desired_x_pos)
            self.y_pos = new_pos

            #We see if max_x is shorter than the line, if so we set it's value normally.
            if max_x < len(buffer.get_line(new_pos)):
                self.x_pos = max_x
                self._desired_x_pos = -1
            #Otherwise we set it to the length of the line and set "_desired_x_pos"
            else:
                self._desired_x_pos = self.x_pos
                self.x_pos = len(buffer.get_line(new_pos))

            return True
            
        else:
            return False


    #Sets the cursor and it's desired position to the start of the line.
    def cursor_start(self) -> None:
        self.x_pos = 0
        self._desired_x_pos = 0


    #Sets the cursor and it's desired position to the end of the line.
    def cursor_end(self, buffer: type[TextBuffer]) -> None:
        pos = len(buffer.get_line(self.y_pos)) - 1
        self.x_pos = pos
        self._desired_x_pos = pos