import yaml
from yaml.loader import SafeLoader
from dataclasses import dataclass


@dataclass
class EditorConfig:
    forget_time: int = None
    tab_size: int = None


#Configuration for the cursor.
@dataclass
class CursorConfig:
    scroll_keys_lines: int = None


#This class contains configuration info pertaining to the buffer display. The Y and X ends are specified from the total height or width
#respectively. For example, a "y_end" of (-2) means that the Y size of the buffer will be the total height of the console window minus 2.
@dataclass
class DisplayConfig:
    #These four configurations are for internal editor use, not configurable by the user.
    y_start: int = 0
    y_end: int = -2
    x_start: int = 0
    x_end: int = 0

    line_number_min_width = None
    statusbar_config = None
    statusbar_separators_definitions = None


#This class contains colour configuration for the various elements in the editor.
@dataclass
class DisplayColourConfig:
    text_colour = None
    cursor_colour = None
    line_number_colour = None
    empty_line_number_colour = None
    status_bar_colour = None
    prompt_colour = None


class ConfigurationHandler:
    def __init__(self):
        self.config_file_name = "./configuration/config.yaml"
        self.config_file = None

        self.load_config_file()


    #Loads the configuration file and stores the info as a dictionary.
    def load_config_file(self) -> None:
        #Open the configuration file.
        with open(self.config_file_name) as file:
            #We use the "SafeLoader" to avoid leaving a security hole that could be exploited.
            self.config_file = yaml.load(file, Loader = SafeLoader)


    #Returns a "EditorConfig" dataclass with the values from the configuration file.
    def get_editor_config(self) -> EditorConfig:
        config = EditorConfig()
        config.forget_time = config.editor_forget_time = self.config_file["editor behaviour"]["editor forget time"]
        config.tab_size = self.config_file["editor behaviour"]["tab size"]

        return config


    #Returns a "CursorConfig" dataclass configured with the values from the configuration file.
    def get_cursor_config(self) -> CursorConfig:
        config = CursorConfig()
        config.scroll_keys_lines = self.config_file["cursor behaviour"]["scroll lines"]

        return config


    #Returns a "DisplayConfig" dataclass with the values from the configuration file.
    def get_display_config(self) -> DisplayConfig:
        config = DisplayConfig()
        config.line_number_min_width = self.config_file["display behaviour"]["line number min width"]
        config.statusbar_config = self.config_file["display behaviour"]["statusbar config"]
        config.statusbar_separators_definitions = self.config_file["display behaviour"]["statusbar separators definitions"]

        return config


    #Returns a "DisplayColourConfig" dataclass with the values from the configuration file.
    def get_display_colour_config(self) -> DisplayColourConfig:
        config = DisplayColourConfig()
        config.text_colour = self.config_file["display colour"]["text colour"]
        config.cursor_colour = self.config_file["display colour"]["cursor colour"]
        config.line_number_colour = self.config_file["display colour"]["line number colour"]
        config.empty_line_number_colour = self.config_file["display colour"]["empty line number colour"]
        config.status_bar_colour = self.config_file["display colour"]["status bar colour"]
        config.prompt_colour = self.config_file["display colour"]["prompt colour"]

        return config