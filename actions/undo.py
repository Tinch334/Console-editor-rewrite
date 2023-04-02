import time
from collections import deque
from typing import Optional

from buffer.buffer import TextBuffer, Line
from buffer.cursor import Cursor


class Undo:
    def __init__(self, snapshot_time: int, max_stack_length: int) -> None:
        #This determines how much time must pass between to actions for the class to consider them separate, in seconds.
        self.snapshot_time = snapshot_time
        #Maximum amount of elements the stack can have, higher numbers mean more undo steps but also more memory consumption.
        self.max_stack_length = max_stack_length

        #A stack is used to store the previous editor states, specifically we are using the "deque" class, a specialized data structure with O(1) time
        #complexity for pushing and popping elements to/from it.
        self.undo_stack = deque()
        #We use this variable because we don't want the last action to be on the undo stack, otherwise the first "Ctrl+Z" wouldn't do anything. Since
        #it would just be replacing the current buffer and cursor with a copy.
        self.undo_to_add = None

        #Time when the last snapshot was taken.     
        self.last_snapshot_time = 0


    #Must be called every time the buffer is modified.
    def undo_handler(self, buffer_value: type[TextBuffer], cursor_value: type[Cursor]) -> None:
        #The last modification occurred more than "self.snapshot_time" seconds ago, we store a new snapshot.
        #           15                      3               1
        if self.last_snapshot_time + self.snapshot_time <= time.time():
            #If the stack is already at it's max length we remove the oldest element in the stack by popping left, to maintain the stacks size.
            if len(self.undo_stack) >= self.max_stack_length:
                self.undo_stack.popleft()

            self.add_undo(buffer_value, cursor_value)

        #Otherwise we replace the last snapshot with the latest changes, since not enough time has passed for a new snapshot. Since we can't replace an
        #element in a "deque" we pop the last element an push the new state.
        else:
            #Make sure there's an element to pop.
            if len(self.undo_stack) > 0:
                self.undo_stack.pop()

            self.add_undo(buffer_value, cursor_value)

        #Set the current time for the snapshot.
        self.last_snapshot_time = time.time()


    #Adds actions to the stack using a buffer.
    def add_undo(self, buffer_value: type[TextBuffer], cursor_value: type[Cursor]) -> None:
        buffer_and_cursor = (buffer_value, cursor_value)

        if self.undo_to_add != None:
            #We add the previous action to the undo stack.
            self.undo_stack.append(self.undo_to_add)

        #We make the current action the one to add the next time a new element is pushed onto the stack.
        self.undo_to_add = buffer_and_cursor


    #Returns a tuple with the last buffer and cursor stored in the undo stack, returns "None" if the stack is empty.
    def get_undo(self) -> Optional[tuple[type[TextBuffer], type[Cursor]]]:
        #Make sure there's an element to pop.
        if len(self.undo_stack) > 0:
            return self.undo_stack.pop()
        else:
            return None