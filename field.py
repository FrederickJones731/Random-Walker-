from walker import *
from UIManager import *
import math

MARGIN = 8
LINE_COUNT_ALLOWED = 400


def create_pos_list(pos: tuple, x: int, y: int) -> list:
    lst = [pos, (pos[0] + x, pos[1]), (pos[0], pos[1] + y),
           (pos[0] + x, pos[1] + y)]

    return lst


class Space(AnimatedImage):

    def __init__(self, space: SpaceType, start_point: tuple, image_list: list,
                 image_size: tuple):
        super().__init__(start_point, image_list, image_size)
        self.__space_type = space

    def get_space_type(self):
        return self.__space_type


class SpaceManager:
    """
    Blackbox class. Is in charge of all the special spaces.
    """

    # gets a tuple - (pos: Position, space_type: portal / end_point / coin / )
    def __init__(self, screen_height: int, screen_width: int):
        self.spaces = list()

        self.height = screen_height
        self.width = screen_width

    def spawn_init_spaces(self, rules_dict: dict, ui_man: UIManager, add_obsts=False) -> None:

        num_portals = rules_dict["portal_num"]
        for i in range(num_portals):
            self.spawn_item(SpaceType.PORTAL, ui_man)

        num_obstacles = rules_dict["obstacle_num"]
        for i in range(num_obstacles):
            self.spawn_item(SpaceType.OBSTACLE, ui_man)

    def spawn_item(self, space_type: SpaceType, ui_man: UIManager):
        """
        Spawns an item to the board. Only Spawns an item if less than 100 items are on field.
        :param ui_man:
        :param space_type:
        :return:
        """
        if len(self.spaces) < 100:
            if space_type == SpaceType.END_GOAL:
                anim_list = ui_man.get_walker_animation(SpaceType.END_GOAL)
                size_tup = anim_list[0].get_size()

                flag_spawn_loc = (((self.width - size_tup[0]) / 2), (self.height - size_tup[1]) / 2)
                flag_space = Space(SpaceType.END_GOAL, flag_spawn_loc, anim_list, size_tup)
                self.__add_item(flag_space)

            else:
                anim_list = ui_man.get_walker_animation(space_type)
                size_tup = anim_list[0].get_size()
                add_space = Space(space_type, self.get_item_spawn_location(size_tup),
                                  anim_list, size_tup)
                self.__add_item(add_space)

    def __get_new_position_lst(self, item_size: tuple) -> list:
        start_x, start_y = item_size[0] + MARGIN, item_size[0] + MARGIN
        end_x, end_y = self.width - start_x, self.height - start_y
        pos = (random.uniform(start_x, end_x), random.uniform(start_y, end_y))
        return create_pos_list(pos, item_size[0], item_size[1])

    def get_item_spawn_location(self, item_size: tuple):

        pos_lst = self.__get_new_position_lst(item_size)
        while self.check_space_collision(pos_lst):
            pos_lst = self.__get_new_position_lst(item_size)

        return pos_lst[0]

    def __add_item(self, sp: Space):
        if not self.check_space_collision(sp.get_corner_positions()):
            self.spaces.append(sp)

    def get_items_in_range(self, pos: tuple, final_pos: tuple):
        obsts = []
        in_range_func = lambda position: self.get_in_range(pos, final_pos, position)

        for item in self.spaces:
            if in_range_func(item.get_position()):
                obsts.append(item)

        return obsts

    def get_in_range(self, init_pos: tuple, final_pos: tuple, pos: tuple) -> bool:
        return init_pos[0] <= pos[0] <= final_pos[0] and init_pos[1] <= pos[1] <= final_pos[1]

    def check_space_collision(self, coords_list: list) -> list:
        hit_obsts = []

        for space in self.spaces:
            if space.collision_check(coords_list) is not None:
                hit_obsts.append(space)

        return hit_obsts

    def remove_child(self, child_to_remove: Space) -> None:
        self.spaces.remove(child_to_remove)


class Field:

    def __init__(self, borders: [list, None], ui_guy: UIManager, game_mode: GameMode, rules_dict: dict, height: int,
                 width: int):
        self.limited = borders is None
        self.borders = borders

        self.walkers = []

        self.height = height
        self.width = width

        self.space_manager = SpaceManager(height, width)
        self.ui_manager = ui_guy

        self.game_mode = game_mode
        self.end_game = False

    def add_walker(self, walker: Walker, game_mode: GameMode, height: int, width: int) -> bool:
        if walker is not None:
            walker.add_aux_vals(self.__get_starting_position(game_mode, height, width),
                                len(self.walkers), height, width, self.ui_manager)
            self.walkers.append(walker)
            return True
        return False

    def spawn_init_spaces(self, rules_dict: dict) -> None:
        self.space_manager.spawn_init_spaces(rules_dict, self.ui_manager, self.game_mode == GameMode.SURVIVAL)

    def init_moves(self) -> True:
        """
        Goes over each walker. Moves them one at a time. If the board is limited, don't go past the walls!
        Makes sure you don't step past obstacles and portals
        :return:
        """
        for walker in self.walkers:
            walker.initiate_move_vals()
            walker.set_max_lines(LINE_COUNT_ALLOWED // self.__alive_walker_count())

    def enact_single_step(self, screen, whizz_mode_on: bool) -> None:
        for walker in self.walkers:
            if walker.get_alive() and self.__check_intersections(walker.get_serial(), screen, whizz_mode_on):
                walker.enact_single_step(screen, whizz_mode_on)
        if not whizz_mode_on:
            for walker in self.walkers:
                walker.draw_walker(screen)

            self.__draw_spaces(screen)

    def __get_starting_position(self, game_mode: GameMode, height: int, width: int) -> tuple:

        if game_mode == GameMode.RACE:
            position_list = [(10, 10), (10, 2 * height / 5),
                             (10, 4 * height / 7), (10, 5.5 * height / 7),
                             (10, 8.5 * height / 10)]

        elif game_mode == GameMode.COPS:
            position_list = [(100, 100), (400, 400),
                             (100, 300), (600, 400),
                             (183, 245)]

        else:
            return self.space_manager.get_item_spawn_location(ICON_SIZE)
        return position_list[len(self.walkers)]

    def __check_intersections(self, walker_id: int, screen, whizz_mode_on: bool) -> bool:
        """
        Checks if the walker hit anything while walking. Borders, portals, obstacles...
        :param walker_id: Current walker id
        :param screen: Screen to print on
        :return: True if hit anything
        """

        if self.game_mode == GameMode.COPS:
            for walker in self.walkers:
                if walker.get_serial() != walker_id:
                    col_pos = self.walkers[walker_id].collision_check(walker.get_collision_pos_list())
                    if col_pos is not None:
                        if self.game_mode == GameMode.COPS and (walker.is_cop() and
                                                                not self.walkers[walker_id].is_cop()):
                            # cops game mode. If a cop catches a robber....
                            self.walkers[walker_id].set_is_cop(True)
                            self.walkers[walker_id].set_animation(self.ui_manager.get_walker_animation("cop"))
                            self.ui_manager.play_caught_sfx()

                            self.walkers[walker_id].end_turn()
                            return False

        if self.borders is not None:
            # check x val on screen
            for pos in self.walkers[walker_id].get_collision_pos_list():
                if (pos[0] < self.borders[0] or pos[0] > self.borders[1] or
                    pos[1] < self.borders[2] or pos[1] > self.borders[3]):
                    if self.game_mode == GameMode.NORMAL:
                        return True
                    elif self.walkers[walker_id].flip_turn(screen, pos,
                                                           (pos[0] < self.borders[0] or pos[0] > self.borders[1]),
                                                           whizz_mode_on):
                        if not whizz_mode_on:
                            self.ui_manager.play_kill_sfx()
                    elif not whizz_mode_on:
                        self.ui_manager.play_bonk_sfx()
                    return False

        spaces = self.space_manager.check_space_collision(self.walkers[walker_id].get_collision_pos_list())

        # assuming hit all obstacles, AND they appear in order:
        for space in spaces:
            type_name = space.get_space_type()

            if type_name == SpaceType.COIN:
                # get coin. add coin to walker, then remove from stage
                self.walkers[walker_id].add_coin()
                self.space_manager.remove_child(space)
                if not whizz_mode_on:
                    self.ui_manager.play_coin_sfx()

            elif type_name == SpaceType.END_GOAL:
                # end goal reached! end game!
                self.end_game = walker_id

            elif type_name == SpaceType.PORTAL:
                if not whizz_mode_on:
                    self.ui_manager.play_portal_sfx()
                self.walkers[walker_id].teleport(self.space_manager.get_item_spawn_location(ICON_SIZE))

            elif type_name == SpaceType.OBSTACLE:
                if not whizz_mode_on:
                    self.ui_manager.play_kill_sfx()

                if self.game_mode != GameMode.SURVIVAL:
                    self.walkers[walker_id].kick_back(screen, whizz_mode_on)
                else:
                    self.walkers[walker_id].kill()

        return True

    def get_end_turn_positions(self) -> list[tuple]:
        """
        returns a list of all current walkers positions. for research purposes
        :return:
        """
        position_list = []
        for walker in self.walkers:
            position_list.append(walker.__start_point)
        return position_list

    # def static_draw(self, screen) -> None:
    #     for walker in self.walkers:
    #         if walker.get_alive():
    #             walker.static_draw(screen)

    def draw_all(self, screen) -> None:
        for walker in self.walkers:
            if walker.get_alive():
                walker.draw_lines(screen)

        for item in self.space_manager.spaces:
            item.draw(screen, False)

        for walker in self.walkers:
            walker.draw_walker(screen)

    def __draw_spaces(self, screen) -> None:
        for space in self.space_manager.spaces:
            space.draw(screen)

    def turn_ongoing(self) -> bool:
        for walker in self.walkers:
            if walker.is_moving():
                return True
        return False

    def toggle_offset(self):
        for walker in self.walkers:
            walker.toggle_offset()

    def __alive_walker_count(self) -> int:
        """
        Get the amount of alive walkers. Helps dictate amount of lines allowed for walkers to draw.
        :return: amount of walkers alive
        """
        count = 0
        for walker in self.walkers:
            if walker.get_alive():
                count += 1
        return count if count != 0 else 1


class InfiniteField(Field):

    def __init__(self, borders: [list, None], ui_guy: UIManager, game_mode: GameMode, rules_dict: dict, height: int,
                 width: int):
        super().__init__(borders, ui_guy, game_mode, rules_dict, height, width)
        self.screen_padding = 0

    def expand_screen(self) -> None:
        """
        Expands the screen if a walker hits the edge of the screen.
        :return: None
        """
        self.screen_padding += 200
        self.borders[0] -= 200
        self.borders[1] += 200
        self.borders[2] -= 200
        self.borders[3] += 200

        for walker in self.walkers:
            walker.padding_shift(self.screen_padding)


class CopsField(Field):

    def __init__(self, borders: [list, None], ui_guy: UIManager, game_mode: GameMode, rules_dict: dict, height: int,
                 width: int):
        super().__init__(borders, ui_guy, game_mode, rules_dict, height, width)

        self.__cop_list, self.__robber_list = [], []
        self.__ratio = -1

    def cops_win(self) -> bool:
        for walker in self.walkers:
            if not walker.is_cop():
                return False

        return True

    def copify(self, ratio: float) -> None:
        """
        Turns selected individuals into cops.
        :param ratio: ratio of cops to robbers (0 to 1)
        :return: A list of all cop ids
        """
        cop_amount = self.__get_cop_amount(ratio)

        cop_list, robber_list = [], []
        for cop_id in range(cop_amount):
            self.walkers[cop_id].set_is_cop(True)
            self.walkers[cop_id].set_animation(self.ui_manager.get_walker_animation("cop"))
            cop_list.append(cop_id)

        for robber_id in range(cop_amount, len(self.walkers)):
            self.walkers[robber_id].set_is_cop(False)
            self.walkers[robber_id].set_animation(self.ui_manager.get_walker_animation("robber"))
            robber_list.append(robber_id)

        self.__cop_list, self.__robber_list = cop_list, robber_list
        self.__ratio = len(cop_list) / (len(cop_list) + len(robber_list))

    def __get_cop_amount(self, ratio: float) -> int:
        if ratio > 1:
            ratio = 1
        elif ratio < 0:
            ratio = 0

        cop_val = math.floor(len(self.walkers) * ratio)

        return cop_val if len(self.walkers) > cop_val > 0 else 1

    def set_winners(self, is_cops: bool) -> None:
        if is_cops:
            for win in self.__cop_list:
                self.walkers[win].set_animation(self.ui_manager.get_walker_animation("winner"))

            for lose in self.__robber_list:
                self.walkers[lose].set_animation(self.ui_manager.get_walker_animation("loser"))
        else:

            for walker in self.walkers:
                if not walker.is_cop():
                    walker.set_animation(self.ui_manager.get_walker_animation("winner"))
                else:
                    walker.set_animation(self.ui_manager.get_walker_animation("loser"))

    def get_cop_ratio(self):
        """
        returns the ratio of cops to all walkers
        :return: ratio, between 0 and 1.
        """
        return self.__ratio


class RaceField(Field):
    def __init__(self, borders: [list, None], ui_guy: UIManager, game_mode: GameMode, rules_dict: dict, height: int,
                 width: int):
        super().__init__(borders, ui_guy, game_mode, rules_dict, height, width)
        self.spawn_flag()

    # race
    def spawn_flag(self):
        self.space_manager.spawn_item(SpaceType.END_GOAL, self.ui_manager)

    def race_completed(self):
        return self.end_game if self.end_game is not False and self.end_game != -1 else False

    def set_winners(self, winners: list, losers: list) -> None:
        for win in winners:
            self.walkers[win].set_animation(self.ui_manager.get_walker_animation("winner"))

        for lose in losers:
            self.walkers[lose].set_animation(self.ui_manager.get_walker_animation("loser"))


class CoinField(Field):

    def __init__(self, borders: [list, None], ui_guy: UIManager, game_mode: GameMode, rules_dict: dict, height: int,
                 width: int):

        self.coin_win_val = rules_dict["coin_win_val"]

        super().__init__(borders, ui_guy, game_mode, rules_dict, height, width)

    def add_coins(self, coin_val: int):
        for i in range(math.floor(coin_val)):
            self.space_manager.spawn_item(SpaceType.COIN, self.ui_manager)
            self.ui_manager.play_spawn_sfx()

    def check_coin_win(self) -> int:
        for walker in self.walkers:
            if walker.get_coin_val() >= self.coin_win_val:
                return walker.get_serial()
        return -1

    def set_winners(self, winners: list, losers: list) -> None:
        for win in winners:
            self.walkers[win].set_animation(self.ui_manager.get_walker_animation("winner"))

        for lose in losers:
            self.walkers[lose].set_animation(self.ui_manager.get_walker_animation("loser"))


class SurvivalField(Field):

    def __init__(self, borders: [list, None], ui_guy: UIManager, game_mode: GameMode, rules_dict: dict, height: int,
                 width: int):
        super().__init__(borders, ui_guy, game_mode, rules_dict, height, width)

    def add_obsts(self, val: int):
        for i in range(math.floor(val)):
            self.space_manager.spawn_item(SpaceType.OBSTACLE, self.ui_manager)

    def check_survival_win(self):
        """
        return winners id val. if more than 2 are alive, game is still going
        :return:
        """
        winner = -1

        for walker in self.walkers:
            if walker.get_alive():
                if winner == -1:
                    winner = walker.get_serial()
                else:
                    return -1

        return winner

    def set_winners(self, winners: list, losers: list) -> None:
        for win in winners:
            self.walkers[win].set_animation(self.ui_manager.get_walker_animation("winner"))

        for lose in losers:
            self.walkers[lose].set_animation(self.ui_manager.get_walker_animation("loser"))
