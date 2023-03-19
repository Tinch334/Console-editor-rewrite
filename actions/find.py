from dataclasses import dataclass
from typing import Optional
import re

from buffer.buffer import TextBuffer


class FindInBuffer:
    def __init__(self, buffer: type[TextBuffer]) -> None:
        self.buffer = buffer


    #Finds all instances of the given regex, then returns them, if none were found returns "None".
    def find_in_buffer(self, regex_to_find: str) -> Optional[dict[int, list[tuple[int, int]]]]:
        matches = {}

        #Gets all matches from all lines.
        for a in range(self.buffer.get_line_count()):
            line_matches = []

            for m in re.finditer(regex_to_find, self.buffer.get_line(a)):
                #The "finditer" function returns a match object with information about the match. We store the span of each match in case they
                #have different lengths.
                line_matches.append(m.span())

            #If a line contains matches we add them to the matches dictionary.
            if line_matches != []:
                matches[a] = line_matches

        if matches != {}:
            return matches
        else:
            return None