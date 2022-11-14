from dataclasses import dataclass, field
from typing import List


@dataclass
class Line:
    contents: str = ""


@dataclass
class TextBuffer:
    buffer: List[Line] = field(default_factory = list)


    def get_char(self, y_pos: int, x_pos: int) -> str:
            try:
                return self.buffer[y_pos][x_pos + 1]

            except:
                return None

    """def get_char(self, y_pos: int, x_pos: int) -> str:
            if (y_pos < length(self.buffer) and x_pos < length(self.buffer[y_pos])):
                return self.buffer[y_pos][x_pos + 1]
            else:
                return None"""



#For testing efficiency.
txt = TextBuffer()
txt.buffer.append(Line("Hola como andas capo"))
txt.buffer.append(Line("Yo bien rey, vos?"))
txt.buffer.append(Line("Todo piola"))

#Works
print(txt.get_char(2, 10))
print(txt.get_char(2, 10))
#Doesn't work
print(txt.get_char(5, 10))
print(txt.get_char(1, 100))