from enum import Enum, auto


class DisplayModesEnum(Enum):
    NORMAL = auto(),
    HIGHLIGHT = auto()



class DisplayModeHandler:
    def __init__(self, colour_config, editor):
        self.colour_config = colour_config
        self.editor = editor

        #We initialize the display modes variable.
        self.current_display_mode = None

        #Highlighted text in highlight mode.
        self.highlight_text = None


    #Displays a character in the given position.
    def display_char(self, display_y: int, display_x: int, actual_y: int, actual_x: int, char: str) -> None:
        match self.current_display_mode:
            case DisplayModesEnum.NORMAL:
                colour = self.editor.get_colour(self.colour_config.text_colour)

            case DisplayModesEnum.HIGHLIGHT:
                #Initially we set the characters colour to the normal colour.
                colour = self.editor.get_colour(self.colour_config.text_colour)

                #We check if there are any characters to highlight in the current line, then we check if the character is in the correct index. If so
                #change the character colour the one for highlighted characters.
                if actual_y in self.highlight_text:
                    for (start, end) in self.highlight_text[actual_y]:
                        if start <= actual_x < end:
                            colour = self.editor.get_colour(self.colour_config.highlight_colour)

        self.editor.stdscr.addstr(display_y, display_x, char, colour)


    #Sets display mode to normal.
    def set_normal_display_mode(self) -> None:
        self.current_display_mode = DisplayModesEnum.NORMAL

    #Sets display mode to highlight mode. The variable "highlight_text" has to be a dictionary containing a key for each line with characters to
    #highlight, and the values to each key should be a list of tuples indicating when the character sections starts and ends.
    def set_highlight_display_mode(self, highlight_text: [dict[int, list[tuple[int, int]]]]) -> None:
        self.current_display_mode = DisplayModesEnum.HIGHLIGHT
        self.highlight_text = highlight_text