from enums import *
import pygame
from enum import Enum


ICON_SIZE = (40, 40)


class SpaceType(Enum):
    COIN = 1
    END_GOAL = 2
    PORTAL = 3
    OBSTACLE = 4


class UIManager:
    """Class for managing UI-related functionalities such as music, sound effects, etc."""

    def __init__(self):
        """Initialize the UIManager with default settings."""
        self.music_on = True
        self.sfx_on = True
        self.game_mode = None

        self.anim_dict = {
            SpaceType.PORTAL: [pygame.transform.scale(pygame.image.load(f"anims/portal{i}.gif"), ICON_SIZE) for i in
                               range(5)],
            SpaceType.END_GOAL: [pygame.transform.scale(pygame.image.load(f"anims/flag{i}.gif"), (100, 170)) for i in
                                 range(3)],
            SpaceType.OBSTACLE: [pygame.transform.scale(pygame.image.load(f"anims/fire{i}.gif"), ICON_SIZE) for i in
                                 range(15)],
            SpaceType.COIN: [pygame.transform.scale(pygame.image.load(f"anims/coin{i}.gif"), ICON_SIZE) for i in
                             range(10)],

            "robber": [pygame.transform.scale(pygame.image.load(f"anims/robber{i}.gif"), (50, 45)) for i in range(12)],
            "cop": [pygame.transform.scale(pygame.image.load(f"anims/police{i}.gif"), ICON_SIZE) for i in range(26)],

            "winner": [pygame.transform.scale(pygame.image.load(f"anims/winner{i}.gif"), ICON_SIZE) for i in range(8)],
            "loser": [pygame.transform.scale(pygame.image.load(f"anims/loser{i}.gif"), ICON_SIZE) for i in range(6)],
            "walker": [
                [pygame.transform.scale(pygame.image.load(f"anims/walker_down{i}.gif"), ICON_SIZE) for i in range(8)],
                [pygame.transform.scale(pygame.image.load(f"anims/walker_left{i}.gif"), ICON_SIZE) for i in range(8)],
                [pygame.transform.scale(pygame.image.load(f"anims/walker_right{i}.gif"), ICON_SIZE) for i in range(8)],
                [pygame.transform.scale(pygame.image.load(f"anims/walker_up{i}.gif"), ICON_SIZE) for i in range(8)]]
        }

    def toggle_music(self):
        """Toggle the background music on/off."""
        self.music_on = not self.music_on
        if self.music_on:
            self.start_music(self.game_mode)
        elif pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    def get_walker_animation(self, space):
        return self.anim_dict[space]
    def toggle_sfx(self):
        """Toggle the sound effects on/off."""
        self.sfx_on = not self.sfx_on

    def start_music(self, game_mode: GameMode):
        """Start playing the background music based on the game mode."""
        self.game_mode = game_mode
        if self.music_on:
            if game_mode == GameMode.RACE:
                pygame.mixer.music.load('sfx/running_theme2.mp3')
            elif game_mode == GameMode.COINS or game_mode == GameMode.NORMAL:
                pygame.mixer.music.load('sfx/coin_run_theme.mp3')
            elif game_mode == GameMode.SURVIVAL or game_mode == GameMode.COPS:
                pygame.mixer.music.load('sfx/survival_theme.mp3')
            elif game_mode == GameMode.MAIN_SCREEN or game_mode == GameMode.GRAPHS:
                pygame.mixer.music.load('sfx/title_theme.mp3')
            pygame.mixer.music.play(-1)

    def end_music(self):
        """Stop playing the background music."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

    def play_coin_sfx(self):
        """Play the sound effect for collecting a coin."""
        if self.sfx_on:
            pygame.mixer.Sound('sfx/coin_sfx.wav').play()

    def play_portal_sfx(self):
        """Play the sound effects for using a portal."""
        if self.sfx_on:
            pygame.mixer.Sound('sfx/portal1.wav').play()
            pygame.mixer.Sound('sfx/portal2.wav').play()

    def play_caught_sfx(self):
        """Play the sound effect for being caught in Cops game."""
        if self.sfx_on:
            pygame.mixer.Sound('sfx/gotcha.wav').play()

    def play_button_click(self):
        """Play the sound effect for clicking a button."""
        if self.sfx_on:
            pygame.mixer.Sound('sfx/button_sfx.wav').play()

    def play_game_over_sfx(self):
        """Play the sound effect for end of game."""
        if self.sfx_on:
            if pygame.mixer.get_busy():
                pygame.mixer.stop()
            pygame.mixer.Sound('sfx/game_over_sfx.mp3').play()

    def play_spawn_sfx(self):
        """Play the sound effect for objects spawning."""
        if self.sfx_on:
            pygame.mixer.Sound('sfx/pop_sfx.flac').play()

    def play_bonk_sfx(self):
        """Play the sound effect for collision."""
        if self.sfx_on:
            pygame.mixer.Sound('sfx/bump_sfx.aiff').play()

    def play_kill_sfx(self):
        """Play the sound effect for dying in Survival Mode."""
        if self.sfx_on:
            pygame.mixer.Sound('sfx/die_sfx.mp3').play()


IMAGE_DELAY = 70


class AnimatedImage:
    """
    Class housing an automatic animator. Given a list of images, it knows to animate them accordingly,
    print them on the screen and know its current location.
    """

    def __init__(self, start_point: tuple, image_list: list, image_size: tuple):

        self.cur_point = start_point
        self.bottom_right_corner = (start_point[0] + image_size[0], start_point[1] + image_size[1])

        self.image_size = image_size
        self.image_list = image_list

        self.count = 0
        self.delay = IMAGE_DELAY
        self.time = 0

    def __animate(self) -> None:
        """
        Decides on the current frame of the animated index. Updates the items time, too.
        :return: Nothing.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.time > self.delay:
            # update time on item
            self.time = current_time
            self.count += 1

            if self.count >= len(self.image_list):
                # reset image index
                self.count = 0

    def draw(self, target_surf, animate=True) -> None:
        """
        Draw the object on the target surface, in the specified location
        :param animate: if it should proceed with animation
        :param target_surf: surface to draw on
        :return: Nothing
        """
        if animate:
            self.__animate()

        target_surf.blit(self.image_list[self.count], (self.cur_point[0], self.cur_point[1]))

    def get_location(self) -> tuple:
        """
        Get current location of the AnimatedImage
        :return: Location, as a tuple (x, y).
        """
        return self.cur_point

    def set_cur_location(self, new_point: tuple) -> bool:
        """
        Set current location for this animated image. Mid-movement generally -
        Doesnt update vertices for end-of movement line
        :param new_point: New location.
        :return: True once completed (Does nothing)
        """
        self.cur_point = new_point
        self.bottom_right_corner = ((self.cur_point[0] + self.image_size[0],
                                    self.cur_point[1] + self.image_size[1]))
        return True

    def collision_check(self, pos_list: list) -> [tuple, None]:
        """
        Gets a list of positions. If any collide with this image's coordinates, returns True
        :param pos_list: List of positions to check for collisions
        :return: True if colliding. False otherwise
        """
        for pos in pos_list:
            if (self.cur_point[0] <= pos[0] <= self.bottom_right_corner[0] and
                    self.cur_point[1] <= pos[1] <= self.bottom_right_corner[1]):
                return (self.cur_point[0] + pos[0]) / 2, (self.cur_point[1] + pos[1]) / 2
        return None

    def get_corner_positions(self) -> list:
        """
        Get the list of all corner positions
        :return: A list of Position objects.
        """
        return [(self.cur_point[0], self.cur_point[1]),
                (self.bottom_right_corner[0], self.cur_point[1]),
                (self.cur_point[0], self.bottom_right_corner[1]),
                (self.bottom_right_corner[0], self.bottom_right_corner[1])]


class MultiAnimatedImage(AnimatedImage):
    """
    An AnimatedImage, which supports multiple animations.
    Image list can be replaced.
    """

    def __init__(self, start_point: tuple, image_list: list, image_size: tuple):
        # here, image list is a list of lists.
        super().__init__(start_point, image_list, image_size)

        self.image_list = []
        self.image_list_storage = []

        self.swap_animation(image_list)

    def swap_animation(self, image_list: list) -> None:
        """
        Switch a given animation, to a different set of animated images.
        :param image_list: new image_list to use as animation
        :return: Nothing
        """
        self.count = 0

        if image_list is not None and isinstance(image_list[0], list) and len(image_list) > 1:
            # if received multiple animations, in form of list of lists in image_list
            self.houses_multiple = True

            self.image_list_storage = image_list
            self.image_list = self.image_list_storage[0]
        else:
            self.houses_multiple = False
            self.image_list = image_list

    def select_animation(self, anim_id_val) -> bool:
        """
        Tells the image which animation should be used.
        :param anim_id_val: 0 = up, 1 = left, 2 = right, 3 = down
        :return: True if switched successfully, False otherwise
        """
        if self.houses_multiple and int(anim_id_val) < len(self.image_list_storage):
            self.image_list = self.image_list_storage[anim_id_val]
            return True
        return False


