
# Console-editor-rewrite
A rewrite of my console editor written in Python using the curses library. The original version can be found [here](https://github.com/Tinch334/Console-editor).

## Requirements
The console editor requires the following:
- Python 3.10 or higher, you can get it [here](https://www.python.org/downloads/).
- The curses module, if you are using Linux you already have it, if instead you use Windows see [windows-curses](https://pypi.org/project/windows-curses/).

## Running
To run the editor first ensure that all the files are in the same folder for the editor to work, including the configuration file. Then do `python console_editor.py"` to run the editor.

## Configuration file
The editor has a configuration file, in YAML. Note that giving fields improper values may break the editor or cause it to not work.

### Colours
You can configure the colour of almost every editor element, the fields in the configuration file that alter an editor colour all end with the word `colour`. When specifying a colour you must follow the format `"<foreground colour>_<background colour>"`. The foreground refers to the colour of the characters, and the background the colour of the character's  background. The available colours for both foreground and background are:
> ``BLACK, BLUE, CYAN, GREEN, MAGENTA, RED, WHITE, YELLOW``

For example the colour `"BLUE_WHITE"` would produce a blue foreground with a white background.

### Configuring the status-bar
The status bar is in the next-to-last line of the editor, it contains useful information, to customise it the `statusbar config` field in the configuration file can be used. This field consists of elements and separators, elements are what display information (filename, line count, cursor position, etc) and separators are what goes between the elements.  The field must start and end with no separator and contain only one right align separator(By default: `/`), other than that you can configure it in any way you want.

#### Elements
Currently there are five available elements:
* `filename:` The name of the file being edited, if it has no name it displays `[No filename]`.
* `lines:` The amount of lines the current file has.
* `modified:` Whether the file has been modified and has unsaved changes.
* `cursor:` Shows the position of the cursor, first vertical then horizontal.
* `time:` Shows the current time in twenty-four hour format.

#### Separators
Separators can be configured and expanded, you can add your own. All the separators the editor recognizes are under `statusbar separators definitions`, they follow the format  `"<identifier>: "<string>"`. Where the identifier is what the editor will look for in `statusbar config`  and string what it will be replaced with in the status-bar. 

The available separators:
* ``\:`` An empty separator, a space will be inserted between the elements.
* ``-:`` The string ``" - "`` will be inserted between the elements.
* ``/:`` The rest of the elements after this separator will be right aligned.

**Note about '/' :** If you look at the value for `/` in the configuration file you will note that it's `-1`, this is what makes it the right align separator. You can change it to be whatever you like, however it's a bad idea to have more than one right align separator.

### Misc configurations
Currently there is one "miscellaneous" option in the editor:
* ``scroll lines:`` It controls how many lines the editor scrolls vertically when the "PgUp" or "PgDown" key is pressed.