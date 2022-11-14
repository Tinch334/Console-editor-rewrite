import utils, curses, curses.ascii
from dataclasses import dataclass
from buffer import TextBuffer
from cursor import Cursor


class Display:
    def __init__(self, buffer: type[TextBuffer], cursor: type[Cursor]) -> None:
        self.buffer = buffer
        self.cursor = cursor


    #This function calls all the different display functions.
    def display(self):
        self.display_buffer()


    #Displays the buffer.
    def display_buffer(self):
        pass