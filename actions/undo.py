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
        #Whether there's an action that needs to be saved.
        self.action_to_save = False


    #This function has to be called every time there's an action that needs to be saved in the undo stack, that way when the "undo_handler" is called
    #in the program loop.
    def set_undo(self) -> None:
        self.action_to_save = True


    #Must be called every time the buffer is modified.
    def undo_handler(self, buffer_value: type[TextBuffer], cursor_value: type[Cursor]) -> None:
        #If the undo stack is empty that means we have either loaded a new file or emptied the queue, to allow the user to undo to this state we add it
        #to the stack.
        if len(self.undo_stack) == 0:
            self._add_undo(buffer_value, cursor_value)
            #When we are storing the base state of the buffer we don't want it to be popped if the user performs an action quickly, therefore we set
            #"last_snapshot_time" to zero, to force a new element to be added to the undo stack. Whilst a flag could be used it would add unnecessary
            #clutter.
            self.last_snapshot_time = 0

            return

        if self.action_to_save:
            #We are saving whatever action caused the flag to be true, we reset it.
            self.action_to_save = False

            #If the last modification occurred less than "self.snapshot_time" seconds ago, we overwrite the last snapshot, to allow the user to undo
            #actions that occurred close together all at once.
            if not self.last_snapshot_time + self.snapshot_time <= time.time():
                #Make sure there's an element to pop.
                if len(self.undo_stack) > 0:
                    self.undo_stack.pop()

            self._add_undo(buffer_value, cursor_value)

            #Set the current time for the snapshot.
            self.last_snapshot_time = time.time()


    #Adds an action to the undo stack.
    def _add_undo(self, buffer_value: type[TextBuffer], cursor_value: type[Cursor]) -> None:
        #If the stack is already at it's max length we remove the oldest element in the stack by popping left, to maintain the stack's size.
        if len(self.undo_stack) >= self.max_stack_length:
            self.undo_stack.popleft()

        buffer_and_cursor = (deepcopy(buffer_value), cursor_value)
        self.undo_stack.append(buffer_and_cursor)
        

    #Returns a tuple with the last buffer and cursor stored in the undo stack, returns "None" if the stack is empty.
    def get_undo(self) -> Optional[tuple[type[TextBuffer], type[Cursor]]]:
        if len(self.undo_stack) > 1:
            #We pop the last element in the undo stack, which corresponds to the current buffer state.
            self.undo_stack.pop()
            return self.undo_stack.pop()
        elif len(self.undo_stack) == 1:
            #If there's only one element left in the queue that means it's the base state of the buffer, we simply return it.
            return self.undo_stack.pop()
        else:
            return None