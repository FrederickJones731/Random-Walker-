import random

from UIManager import *
from enum import Enum
import math

ANIM_OFFSET = 5

TURN_LENGTH = 300


class MoveType(Enum):
    CARDINAL = 1
    FREE = 2
    BIASED = 3


class Direction(Enum):
    UP = 0
    LEFT = 1
    RIGHT = 2
    DOWN = 3


color_list = [
    (65, 97, 125),  # blue, p1
    (99, 55, 55),  # red, p2
    (133, 124, 76),  # yellow, p3
    (54, 92, 57),  # groen, p4
    (135, 86, 135),  # pink, p5
]


class WalkerVisuals(MultiAnimatedImage):

    def __init__(self, pos: tuple, image_list: list, char_color: tuple, image_size: tuple,
                 screen_height: int, screen_width: int, location_list: list):
        super().__init__(pos, image_list, image_size)

        # self.__max_line_length = 160
        self.__ongoing = False
        self.__offset = 0
        self.__offset_cycle = 0
        self.__mind_offset = True

        self.__start_point = pos
        self.__end_point = None

        self.__location_list = location_list
        self.__char_color = char_color

        self.__roots = None
        self.__step_count = 0

        self.__direction = None

        self.__scr_height = screen_height
        self.__scr_width = screen_width
        self.padding = 0

    def set_animation(self, anim: list) -> bool:
        if isinstance(anim, list):
            self.swap_animation(anim)
            return True
        return False

    def set_data(self, step: Step) -> None:
        self.__roots = self.__find_roots(step)
        self.__start_point = self.cur_point

        self.__offset_cycle = self.__calc_offset(step[1])
        self.__ongoing = True

    def step(self, screen, whizz_mode_on: bool) -> None:
        """
        Gets applied starting point from what is set in the object.
        Draws a line from that point, to the given end point
        :param screen: the screen. draws on here
        :return: Nothing
        """

        temp_point = (self.cur_point[0], self.cur_point[1])

        if self.__step_count > 0:
            # get the new value for cur_point, take a step if offset is good / should zoom
            if whizz_mode_on or (not self.__mind_offset) or self.__offset == self.__offset_cycle:
                self.__offset = 0

                temp_point = self.get_temp_point(temp_point, whizz_mode_on)

                # if self.__check_stop(temp_point):
                #     self.__ongoing = False
            else:
                self.__offset += 1

        temp_point = self.get_aliased_position(temp_point)

        if not whizz_mode_on:
            self.draw_lines(temp_point, screen)
        self.set_cur_location(temp_point)

    def get_temp_point(self, pos: tuple, whizz_mode_on: bool) -> tuple:

        temp_point = (pos[0] + self.__roots[0], pos[1] + self.__roots[1])
        self.__step_count -= 1

        while whizz_mode_on and self.__step_count > 0:
            temp_point = (temp_point[0] + self.__roots[0], temp_point[1] + self.__roots[1])
            self.__step_count -= 1

        return temp_point

    def flip_turn(self, screen, hor_collision: bool, whizz_mode_on: bool) -> None:
        """
        reverses a single step, when hitting something. Immediately ends turn.
        :param whizz_mode_on: if should play music, draw sfx...
        :param hor_collision: if an impact was made from the horizontal side (determines how this walker flips)
        :param screen: screen to draw on
        :return: Nothing
        """
        temp_point = (self.cur_point[0], self.cur_point[1])
        temp_point = (temp_point[0] - self.__roots[0], temp_point[1] - self.__roots[1])

        self.__step_count += 1
        if not hor_collision:
            self.__roots = (self.__roots[0], -self.__roots[1])
        else:
            self.__roots = (-self.__roots[0], self.__roots[1])

        self.__set_walker_direction(self.__roots[0], self.__roots[1])

        temp_point = self.get_aliased_position(temp_point)

        if not whizz_mode_on:
            self.draw_lines(temp_point, screen)
        self.set_cur_location(temp_point)

    def kick_back(self, screen, whizz_mode_on: bool) -> None:
        temp_point = (self.cur_point[0], self.cur_point[1])
        temp_point = (temp_point[0] - 20 * self.__roots[0], temp_point[1] - 20 * self.__roots[1])

        self.end_turn()

        temp_point = self.get_aliased_position(temp_point)

        if not whizz_mode_on:
            self.draw_lines(temp_point, screen)
        self.set_cur_location(temp_point)

    def teleport(self, final_pos: tuple):
        self.cur_point = self.get_aliased_position(final_pos)

    def get_aliased_position(self, position: tuple) -> tuple:
        pos_x = self.padding + (self.__scr_height / (self.__scr_height + 2 * self.padding)) * position[0]
        pos_y = self.padding + (self.__scr_width / (self.__scr_width + 2 * self.padding)) * position[1]

        return pos_x, pos_y

    def set_start_position(self, pos: tuple) -> None:
        self.__start_point = pos

    def toggle_offset(self) -> None:
        self.__mind_offset = not self.__mind_offset

    def is_ongoing(self):
        return not self.__step_count <= 0

    def end_turn(self):
        self.__step_count = 0
        self.__end_point = self.get_aliased_position(self.cur_point)

    def moving_horizontally(self) -> bool:
        """
        Returns true if is moving horizontally
        :return: True if moving horizonally
        """
        return self.__direction == Direction.RIGHT or self.__direction == Direction.LEFT

    def draw_lines(self, cur_point: tuple, screen) -> None:
        """
        Draws a line from the walker UI's starting point, to the current point. Also prints the walkers current image
        :param cur_point: point to match the line to
        :param screen: the screen,to print on
        :return: Nothing
        """

        vertex_index = 1
        while vertex_index < len(self.__location_list):
            pygame.draw.line(screen, self.__char_color,
                             self.get_aliased_position(self.__location_list[vertex_index - 1]),
                             self.get_aliased_position(self.__location_list[vertex_index]), 4)
            vertex_index += 1

        start_pos = self.__start_point[0] + ANIM_OFFSET, self.__start_point[1] + ANIM_OFFSET
        cur_pos = cur_point[0] + ANIM_OFFSET, cur_point[1] + ANIM_OFFSET

        start_pos = self.get_aliased_position(start_pos)
        cur_pos = self.get_aliased_position(cur_pos)

        alt_start = (start_pos[0], start_pos[1] + 2)
        alt_end = (cur_pos[0], cur_pos[1] + 2)

        alt_start = self.get_aliased_position(alt_start)
        alt_end = self.get_aliased_position(alt_end)

        blue = (95, 202, 245, 60)
        dark_blue = (46, 74, 166)

        pygame.draw.line(screen, blue, start_pos, cur_pos, 6)
        pygame.draw.line(screen, dark_blue, alt_start, alt_end, 2)

    def draw_walker(self, screen, is_alive=True, animate=True):
        if is_alive:
            if self.__direction is None:
                self.__set_walker_direction(0, 0)
            self.select_animation(self.__direction.value)
            self.draw(screen, animate)

    def __find_roots(self, step: Step) -> tuple:

        angle = step[0]
        hypotenuse = step[1]

        x, y = math.sin(math.radians(angle)) * hypotenuse, math.cos(math.radians(angle)) * hypotenuse

        step_count = math.floor(hypotenuse)

        if step_count == 0:
            step_count = 1

        self.__set_walker_direction(x, y)
        self.__step_count = step_count

        return x / hypotenuse, y / hypotenuse

    def __set_walker_direction(self, x: float, y: float) -> None:
        if abs(x) > abs(y):
            self.__direction = Direction.RIGHT if x > 0 else Direction.LEFT
        else:
            self.__direction = Direction.UP if y > 0 else Direction.DOWN

    def __calc_offset(self, step_size: float) -> int:
        return math.ceil(TURN_LENGTH / step_size)


class Walker:
    """
    The walker object. Stores position, moves around and has its own filters telling it how to move.
    Is also in charge of its visuals, and tracking data later to be used in the graphs
    """

    def __init__(self, step_range_lst: list, filters: list[any]):
        self.__min_step = step_range_lst[0] if step_range_lst[0] > 0 else 1
        self.__max_step = step_range_lst[1] if step_range_lst[1] > step_range_lst[0] else self.__min_step + 1

        self.__move_type = self.__get_move_type(filters[0], filters[1])
        if self.__move_type == MoveType.BIASED:
            self.__dir_bias = filters[1]
        else:
            self.__dir_bias = None

        self.__max_lines = 0

        self.__coin_val = 0
        self.__is_active = True
        self.__is_cop = False

        self.__obstacles_hit = 0
        self.__portals_used = 0

        self.position = None
        self.spawn_position = None
        self.index_val = -1

        self.__stuck_counter = 0

        self.__visuals = None
        self.location_list = []

    def add_aux_vals(self, position: tuple, index_val: int, screen_height: int, screen_width: int, man: UIManager):
        self.position = position
        self.spawn_position = position
        self.index_val = index_val

        self.__visuals = WalkerVisuals(self.position, man.get_walker_animation("walker"), color_list[index_val], ICON_SIZE,
                                        screen_height, screen_width, self.location_list)

        self.add_vertex(self.spawn_position)

    def get_serial(self):
        return self.index_val

    def get_spawn_position(self) -> tuple:
        return self.spawn_position

    def set_max_lines(self, max_lines: int) -> None:
        """
        Set maximum amount of lines the walker is allowed to draw.
        :param max_lines: said amount.
        :return: None
        """
        self.__max_lines = max_lines

    def initiate_move_vals(self) -> bool:
        """
        if walker is mid-movement, do nothing.
        otherwise, enter movement parameters.
        :return: True if parameters were accepted
        """
        if self.__visuals.is_ongoing():
            return False

        self.add_vertex(self.position)
        self.__visuals.set_data(self.get_step_data())

        return True

    def enact_single_step(self, screen, whizz_mode_on: bool):
        if self.__is_active:
            self.__stuck_counter = 0
            return self.__visuals.step(screen, whizz_mode_on)

    def draw_lines(self, screen):
        self.__visuals.draw_lines(self.get_position(), screen)

    def draw_walker(self, screen):
        self.__visuals.draw_walker(screen, self.__is_active, True)

    def get_step_data(self) -> Step:
        """
        to be called from outside the runner.
        :return: direction and next step size of the next step
        """
        dir = self.__get_direction()
        return dir, self.__get_step_size()

    def is_moving(self):
        if self.__is_active:
            if self.__visuals.is_ongoing():
                return True
            else:
                self.position = self.__visuals.get_location()
                return False
        else:
            return False

    def end_turn(self):
        self.__visuals.end_turn()

    def add_vertex(self, vertex: tuple) -> None:
        self.location_list.append(vertex)
        while len(self.location_list) > self.__max_lines:
            self.location_list.pop(0)

    def get_collision_pos_list(self) -> list:
        return self.__visuals.get_corner_positions()

    def set_animation(self, anim: list) -> None:
        self.__visuals.set_animation(anim)

    def get_moving_horizontally(self) -> bool:
        return self.__visuals.moving_horizontally()

    def __get_move_type(self, val: int, bias: float) -> MoveType:
        if val == 1:
            return MoveType.CARDINAL
        elif not (isinstance(bias, float) or isinstance(bias, int)):
            raise TypeError("Incorrect Walker-bias inserted in json file!")
        elif val == 3 and 360 >= bias >= 0:
            return MoveType.BIASED
        return MoveType.FREE

    def __get_biased_direction(self):

        bias = self.__dir_bias

        if self.__move_type == MoveType.CARDINAL:
            if 90 <= bias <= 270:
                return int(random.uniform(1, 2.99)) * 90 if bias < 180 else int(random.uniform(2, 3.99)) * 90
            else:
                return int(random.uniform(0, 1.99)) * 90 if bias < 90 else int(random.uniform(3, 4.99)) * 90

        random_val = random.uniform(0, 1)

        if random_val < 0.1:
            return bias
        elif random_val < 0.5:
            return (bias + random.uniform(-40, 40)) % 360
        elif random_val < 0.7:
            return (bias + random.uniform(-100, 100)) % 360
        else:
            return random.uniform(0, 360)

    def __get_direction(self) -> [float, float]:
        """
        Generates a random, 2d direction to take the next step in.
        :return: A Vector in form.
        """
        if self.__dir_bias is None:
            if self.__move_type == MoveType.CARDINAL:
                # only for moving in a cardinal direction bot
                return 90 * int(random.uniform(0, 4.99))
            return random.uniform(0, 360)
        else:
            return self.__get_biased_direction()

    def __get_step_size(self) -> float:
        """
        Get the size of the next step. Psuedo-randomly. Takes into account the min-max sizes allowed.
        :return: Size of the next step in form of a float
        """
        x = random.uniform(self.__min_step, self.__max_step)
        return x if not self.__is_cop else x * 2

    def collision_check(self, corner_pos_list: list) -> [tuple, None]:
        if self.__is_active:
            return self.__visuals.collision_check(corner_pos_list)
        return None

    def get_position(self) -> tuple:
        return self.position

    def padding_shift(self, padding_val) -> None:
        self.__visuals.padding = padding_val

    # minigame functions

    def is_cop(self) -> bool:
        return self.__is_cop

    def set_is_cop(self, res: bool) -> None:
        self.__is_cop = res

    def add_coin(self) -> int:
        self.__coin_val += 1

        return self.__coin_val

    def get_coin_val(self):
        return self.__coin_val

    def kill(self):
        self.__is_active = False

    # movement types
    def teleport(self, final_pos: tuple) -> None:
        self.__portals_used += 1
        self.add_vertex(self.position)
        self.position = final_pos

        self.__visuals.teleport(final_pos)

    def flip_turn(self, screen, hit_pos: tuple, hor_collision: bool, whizz_mode_on: bool) -> bool:
        """
        Flips the char around, bumping them in another different angle. If walker is stuck, reset position
        :param whizz_mode_on: if music should play, draw things on screen, or just whizz past everything
        :param screen: Screen to print on
        :param hit_pos: the position in which the char was hit in
        :param hor_collision: If the walker should reverse their horizontal momentum, or vertical
        :return: True if has been bumped 5 times consecutively -> reset spawn
                false for a normal flip turn
        """
        self.__visuals.flip_turn(screen, hor_collision, whizz_mode_on)

        self.add_vertex(hit_pos)
        self.__visuals.set_start_position(hit_pos)

        self.__stuck_counter += 1

        if self.__stuck_counter >= 5:
            self.__reset_position()
            return True

        return False

    def kick_back(self, screen, whizz_mode_on: bool) -> None:
        """
        Enact the kick back effect when hitting an obstacle
        :param screen: screen to print on
        :param whizz_mode_on: if music should play, draw things on screen, or just whizz past everything
        :return: None
        """
        self.__obstacles_hit += 1

        self.add_vertex(self.position)
        self.__visuals.kick_back(screen, whizz_mode_on)

    def __reset_position(self) -> None:
        self.position = self.spawn_position
        self.__visuals.teleport(self.spawn_position)

    def get_alive(self):
        return self.__is_active

    def toggle_offset(self):
        self.__visuals.toggle_offset()

    # research functions
    def get_portals_used_count(self):
        """
        Get portals used this game.
        :return: Num of portals used.
        """
        return self.__portals_used

    def get_obstacles_hit_count(self):
        """
        Get obstacles hit this game.
        :return: Num of obstacles hit.
        """
        return self.__obstacles_hit

    def get_final_loc_list(self):
        return self.location_list
