import os.path
from dataclasses import dataclass
from typing import Optional

from buffer.buffer import Line, TextBuffer


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


    #Takes a buffer and saves it to the specified "filename", returns the number of bytes written if no errors occurred. If an error occurred it
    #returns "-1".
    def save_file(self, buffer: type[TextBuffer], filename: str, line_ending: str = "\n") -> int:
        #This try block is to avoid creating a security hole that might allow a user to access files without permission.
        try:
            path = os.path.join(os.getcwd(), filename)
            file = open(filename, "w")

        #In case an error occurred.
        except:
            return -1
        else:   
            #If the file could be opened/created set the filename.
            self.filename = filename

            #We read each line in the buffer and write it to the file, adding the corresponding line ending.
            for y in range(0, buffer.get_line_count()):
                    file.write(buffer.get_line(y) + line_ending)
            
            file.close()

            #If the file was closed successfully that means that it was saved correctly, therefore the buffer is no longer different from the
            #file
            self.dirty = False

            #No errors occurred, return the number of bytes written to disk.
            return os.path.getsize(path)


    #Takes a buffer and a filename, it then stores the file in the buffer, returns the number of bytes read if no errors occurred. If an error
    #occurred it returns "-1".
    def load_file(self, buffer: type[TextBuffer], filename: str) -> list[Line] | int:
        #This try block is to avoid creating a security hole that might allow a user to access files without permission.
        try:
            path = os.path.join(os.getcwd(), filename)
            file = open(filename, "r")

        #In case an error occurred.
        except:
            return -1
        else:
            #If the file could be opened set the filename.
            self.filename = filename
            file_contents = []

            for line in file.readlines():
                #We remove newlines from the file in case there are any.
                line = line.replace("\n", "")
                #We add the line to the temporary buffer.
                file_contents.append(Line(line))

            #We set the editor buffer to the loaded buffer.
            buffer.set_buffer(file_contents)    

            #Since we've just loaded a file it's unmodified, it's no longer dirty.
            self.dirty = False

            #If the file was closed successfully that means that it was opened and read correctly, return the number of bytes read.
            return os.path.getsize(path)