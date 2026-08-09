import json
import random
from typing import Dict, List, Tuple, Union

import pygame as py

from UIManager import *
from enums import *
from game import get_game_object

DataList = List[Union[int, str]]
WalkerConfig = List[Union[int, DataList]]

def load_json(filename: str) -> Dict[str, WalkerConfig]:
    """
    This function opens a JSON file and loads its content.
    :param filename: path to the json file.
    :return: A dictionary containing the content of the JSON file.
    """
    with open(filename, 'r') as json_file:
        dict_config: Dict[str, WalkerConfig] = json.load(json_file)

    return dict_config

def get_background_image(game_mode: GameMode, height: int, width: int) -> py.Surface:
    """
    Get the applicable background for the current gameMode activity.
    :param game_mode: gameMode, in which we will determine the bg to return
    :param height: screen height (for transformation purposes)
    :param width: screen width (for transformation purposes)
    :return: Appropriate background image
    """
    image = None
    if game_mode == GameMode.GRAPHS:
        # get graph activity background
        image = py.image.load("anims/graph_back.jpg")
    elif game_mode == GameMode.MAIN_SCREEN:
        # get main screen background
        image = py.image.load("anims/title_back.jpg")
    else:
        # game screens. Get random background image
        rand = int(random.uniform(0, 3.99))
        if rand == 0:
            image = py.image.load("anims/back1.webp")
        elif rand == 1:
            image = py.image.load("anims/back2.jpg")
        elif rand == 2:
            image = py.image.load("anims/back3.jpg")
        elif rand == 3:
            image = py.image.load("anims/back4.jpg")

    # Scale the image to fit the screen
    return py.transform.scale(image, (width, height))


class Screen:
    """
    Screen class represents a screen in the game.
    """
    def __init__(self, width: int, height: int, music: UIManager):
        """
        Initialize the Screen object.
        :param width: Width of the screen.
        :param height: Height of the screen.
        :param music: UIManager object for managing music.
        """
        self.height = height
        self.width = width
        self.__is_active = False
        self.screen = None
        self.music = music
        # default value
        self.game_mode = GameMode.MAIN_SCREEN
        self.background = py.Surface((width, height))

    def make_cur_screen(self, game_mode: GameMode, ui_man: UIManager, end_music=True) -> None:
        """
        Makes the selected screen, showing it over the others.
        :param game_mode: Game mode of the screen.
        :param ui_man: UIManager object.
        :return: None
        """
        self.game_mode = game_mode
        self.background = get_background_image(self.game_mode, self.height, self.width)
        self.__is_active = True
        self.screen = py.display.set_mode((self.width, self.height))

        walker_dict = load_json("walker_config.json")
        rules_dict = load_json("rules_config.json")
        dim_tuple = (self.width, self.height)

        if game_mode != GameMode.GRAPHS:
            self.game = get_game_object(game_mode, walker_dict, rules_dict, ui_man, dim_tuple)
            self.game.spawn_init_spaces(rules_dict)

        if end_music:
            self.music.end_music()
            self.music.start_music(game_mode)

    def end_current_screen(self) -> None:
        """
        Kills current screen.
        :return: None
        """
        self.__is_active = False

    def is_active(self) -> bool:
        """
        Check if the screen is active.
        :return: True if the screen is active, False otherwise.
        """
        return self.__is_active


class TextBox:

    def __init__(self, x: float, y: float, sx: float, sy: float,
                 fcolour: Tuple[int, int, int], text: str, font_size: int = 25, is_title=False) -> None:
        """
        Initialize the Button object.
        :param x: x-coordinate of the button.
        :param y: y-coordinate of the button.
        :param sx: Width of the button.
        :param sy: Height of the button.
        :param fcolour: Color of the button font.
        :param text: Text to display on the button.
        :param font_size: Font size of the button text.
        """
        self.x = x
        self.y = y
        self.sx = sx
        self.sy = sy

        self.text = text
        self.__fontsize = font_size
        self.font_colour = fcolour
        self.font = py.font.SysFont("Arial", self.__fontsize)

        self.button_back_color = (0, 0, 0)
        self.screen_is_active = False
        self.is_clicked = False

    def show(self, screen: py.Surface) -> None:
        """
        Show the button on the screen.
        :param screen: The screen to display the button.
        :return: None
        """
        py.draw.rect(screen, (40, 40, 40), (self.x, self.y, self.sx, self.sy))
        textsurface = self.font.render(self.text, False, self.font_colour)

        text_width = len(self.text) * self.__fontsize // 2
        text_x = self.x + (self.sx // 2) - (text_width // 2)
        text_y = (self.y + (self.sy / 2) - (self.__fontsize / 2) - 4)

        screen.blit(textsurface, (text_x, text_y))


class Button(TextBox):
    """
    Button Class. Allows to form a whenever necessary, deals with UI too.
    """

    def __init__(self, link: Enum, x: float, y: float, sx: float, sy: float, fcolour: Tuple[int, int, int], text: str,
                 font_size: int = 25) -> None:
        """
        Initialize the Button object.
        :param link: Enum indicating the link.
        :param x: x-coordinate of the button.
        :param y: y-coordinate of the button.
        :param sx: Width of the button.
        :param sy: Height of the button.
        :param fcolour: Color of the button font.
        :param text: Text to display on the button.
        :param font_size: Font size of the button text.
        """
        super().__init__(x, y, sx, sy, fcolour, text, font_size)
        self.link = link

    def is_being_clicked(self, mouse_pos: Tuple[int, int], is_clicked: bool) -> bool:
        """
        Check if the button is currently being clicked.
        :param mouse_pos: Current position of the mouse.
        :param is_clicked: Boolean indicating if the mouse is clicked.
        :return: True if the button is clicked, False otherwise.
        """
        if not self.is_clicked and (self.x <= mouse_pos[0] <= self.x + self.sx and
                                    self.y <= mouse_pos[1] <= self.y + self.sy):
            self.screen_is_active = True
            if is_clicked:
                self.is_clicked = True
            return is_clicked
        else:
            self.screen_is_active = False
            if not is_clicked:
                self.is_clicked = False
            return False

    def get_link(self) -> Enum:
        """
        Get the link of the button.
        :return: The link of the button.
        """
        return self.link


class ImageButton(Button):
    """
    ImageButton class represents a button with an image.
    """
    def __init__(self, link: Enum, x: float, y: float, sx: float, sy: float,
                 fcolour: Tuple[int, int, int], image: py.Surface) -> None:
        """
        Initialize the ImageButton object.
        :param link: Enum indicating the link.
        :param x: x-coordinate of the button.
        :param y: y-coordinate of the button.
        :param sx: Width of the button.
        :param sy: Height of the button.
        :param fcolour: Color of the button font.
        :param image: Image of the button.
        """
        super().__init__(link, x, y, sx, sy, fcolour, "")

        self.image = image

    def show(self, screen: py.Surface) -> None:
        """
        Show the button on the screen.
        :param screen: The screen to display the button.
        :return: None
        """
        py.draw.rect(screen, (40, 40, 40), (self.x, self.y, self.sx, self.sy))
        screen.blit(self.image, (self.x, self.y))
