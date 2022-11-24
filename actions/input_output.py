import os.path
from dataclasses import dataclass
from typing import Optional

from buffer.buffer import TextBuffer


@dataclass
class IOHandler:
    filename: str = None
    #Determines whether the buffer has been modified or not.
    dirty: bool = False


    #Sets the dirty flag to "True".
    def set_dirty(self) -> None:
        self.dirty = True


    #Returns whether the buffer is "dirty" or not.
    def get_dirty(self) -> bool:
        return self.dirty


    def get_filename(self) -> str:
        return self.filename


    #Takes a buffer and saves it to the specified "filename", returns "0" if no errors occurred. If no filename was specified and no filename
    #was provided it returns "-1", if an access/permission error occurred it returns "-2".
    def save_file(self, buffer: type[TextBuffer], filename: Optional[str] = None, line_ending: str = "\n") -> int:
        #If there's no supplied filename and it's not set in the class then we don't have any way of getting the filename, return an error.
        if filename == None and self.filename == None:
            return -1
        elif filename != None:
            self.filename = filename

        #This try block is to avoid creating a security hole that might allow a user to access files without permission.
        try:
            path = os.path.join(os.getcwd(), self.filename)
            file = open(self.filename, "w")

        #In case the user doesn't have permission or some other error occurred.
        except:
            return -2
        else:

            #We read each line in the buffer and write it to the file, adding the corresponding line ending.
            for y in range(0, buffer.get_line_count()):
                    file.write(buffer.get_line(y) + line_ending)
            
            file.close()
            #If the file was closed successfully that means that it was saved correctly, therefore the buffer is no longer different from the
            #file, it's no longer dirty.
            self.dirty = False

            #No errors occurred, return 0.
            return 0