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



    def display_char(self, y, x, char) -> None:
        match self.current_display_mode:
            case DisplayModesEnum.NORMAL:
                self.editor.stdscr.addstr(y, x, char, self.editor.get_colour(self.colour_config.text_colour))

            case DisplayModesEnum.HIGHLIGHT:
                self.editor.stdscr.addstr(y, x, char, self.editor.get_colour(self.colour_config.highlight_colour))


    #Sets display mode to normal.
    def set_normal_display_mode(self) -> None:
        self.current_display_mode = DisplayModesEnum.NORMAL


    def set_highlight_display_mode(self, highlight_text: [dict[int, list[tuple[int, int]]]]) -> None:
        self.current_display_mode = DisplayModesEnum.HIGHLIGHT
        self.highlight_text = highlight_text