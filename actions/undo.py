import time
from collections import deque
from typing import Optional
from copy import deepcopy

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

        #Time when the last snapshot was taken.     
        self.last_snapshot_time = 0


    #Must be called every time the buffer is modified.
    def undo_handler(self, buffer_value: type[TextBuffer], cursor_value: type[Cursor]) -> None:
        self.action_to_save = False

        #The last modification occurred more than "self.snapshot_time" seconds ago, we store a new snapshot.
        if self.last_snapshot_time + self.snapshot_time <= time.time():
            #If the stack is already at it's max length we remove the oldest element in the stack by popping left, to maintain the stacks size.
            if len(self.undo_stack) >= self.max_stack_length:
                self.undo_stack.popleft()

        #Otherwise we replace the last snapshot with the latest changes, since not enough time has passed for a new snapshot. Since we can't
        #replace an element in a "deque" we pop the last element an push the new state.
        else:
            #Make sure there's an element to pop.
            if len(self.undo_stack) > 0:
                self.undo_stack.pop()

        self.add_undo(buffer_value, cursor_value)

        #Set the current time for the snapshot.
        self.last_snapshot_time = time.time()


    def add_undo(self, buffer_value: type[TextBuffer], cursor_value: type[Cursor]) -> None:
        buffer_and_cursor = (deepcopy(buffer_value), cursor_value)
        self.undo_stack.append(buffer_and_cursor)
        

    #Returns a tuple with the last buffer and cursor stored in the undo stack, returns "None" if the stack is empty.
    def get_undo(self) -> Optional[tuple[type[TextBuffer], type[Cursor]]]:
        #raise Exception(self.undo_stack)

        if len(self.undo_stack) > 1:
            self.undo_stack.pop()
            return self.undo_stack.pop()
        elif len(self.undo_stack) == 1:
            return self.undo_stack.pop()
        else:
            return None