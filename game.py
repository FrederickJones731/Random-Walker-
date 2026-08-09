from field import *
from walker import *

FieldType = [Field, CoinField, CopsField, RaceField, SurvivalField, InfiniteField]

BLACK = (0, 0, 0)
BLUE = (95, 202, 245, 60)
DARK_BLUE = (46, 74, 166)
WHITE = (255, 255, 255)


def check_valid_rules_dict(rd: dict) -> None:
    """
    Make sure the rules dictionary json file is valid.
    Fills default values for missing keys
    :param rd: rules_dict
    :return: Nothing
    """
    if "survival_add_interval" in rd.keys():
        if not (isinstance(rd["survival_add_interval"], int)):
            raise TypeError("Invalid Type for obstacle interval add val! Must be an int!")
        elif rd["survival_add_interval"] < 1:
            raise ValueError("Enter only positive numbers into add-turn intervals!")
    else:
        rd["survival_add_interval"] = 3

    if "obstacles_per_interval" in rd.keys():
        if not (isinstance(rd["obstacles_per_interval"], int)):
            raise TypeError("Invalid Type for obstacle added per interval!")
        elif rd["obstacles_per_interval"] < 1:
            raise ValueError("Enter only positive numbers into obstacles added per turn!")
    else:
        rd["obstacles_per_interval"] = 5

    if "coin_add_interval" in rd.keys():
        if not (isinstance(rd["coin_add_interval"], int)):
            raise TypeError("Invalid Type for coin interval add val! Must be an int!")
        elif rd["coin_add_interval"] < 1:
            raise ValueError("Enter only positive numbers into add-turn intervals (coin)!")
    else:
        rd["coin_add_interval"] = 1

    if "coins_per_interval" in rd.keys():
        if not (isinstance(rd["coins_per_interval"], int)):
            raise TypeError("Invalid Type for coins added per interval!")
        elif not 0 <= rd["coins_per_interval"] <= 50:
            raise ValueError("Coins added per interval must be between 0 and 50!")
    else:
        rd["coins_per_interval"] = 4

    if "init_coin_val" in rd.keys():
        if not (isinstance(rd["init_coin_val"], int)):
            raise TypeError("Initial coins added num must be an integer!")
        elif not 100 >= rd["init_coin_val"] >= 0:
            raise ValueError("Init coins added must be between 0 and 100!")
    else:
        rd["init_coin_val"] = 30

    if "coin_win_val" in rd.keys():
        if not (isinstance(rd["coin_win_val"], int)):
            raise TypeError("Coin Win Val added num must be an integer!")
        elif not rd["coin_win_val"] > 0:
            raise ValueError("Coin win val must be a positive integer!")
    else:
        rd["coin_win_val"] = 10

    if "cops_game_length" in rd.keys():
        if not (isinstance(rd["cops_game_length"], int)):
            raise TypeError("Cops game length must be an integer!")
        elif not rd["cops_game_length"] > 0:
            raise ValueError("Cops game length must be a positive integer!")
    else:
        rd["cops_game_length"] = 40

    if "infinite_walker_length" in rd.keys():
        if not (isinstance(rd["infinite_walker_length"], int)):
            raise TypeError("Infinite runner walk length must be an integer!")
        elif not rd["infinite_walker_length"] > 0:
            raise ValueError("Infinite runner game length must be a positive integer!")
    else:
        rd["infinite_walker_length"] = 100
    if "portal_num" in rd.keys():
        if not isinstance(rd["portal_num"], int):
            raise TypeError("Num portals must be an integer! (.json!)")
        elif not 10 >= rd["portal_num"] >= 0:
            raise ValueError("Num portals must be between 0 and 10! (.json!)")
    else:
        rd["portal_num"] = 3

    if "obstacle_num" in rd.keys():
        if not isinstance(rd["obstacle_num"], int):
            raise TypeError("Num obstacles must be an integer! (.json!)")
        elif not 10 >= rd["obstacle_num"] >= 0:
            raise ValueError("Num obstacles must be between 0 and 10! (.json!)")
    else:
        rd["obstacle_num"] = 3

    if "cop_robber_ratio" in rd.keys():
        if not isinstance(rd["cop_robber_ratio"], float):
            raise TypeError("Cop to robber ratio must be a float!")
        elif not 1 > rd["cop_robber_ratio"] > 0:
            raise ValueError("Cops to robbers ratio must be between 0 and 1!")
    else:
        rd["cop_robber_ratio"] = 0.4

class Game:

    def __init__(self, game_mode: GameMode, walker_dict: dict, rules_dict: dict, music: UIManager, screen_dim: tuple):
        height, width = screen_dim[1], screen_dim[0]

        check_valid_rules_dict(rules_dict)

        self.music_manager = music

        self.rules_dict = rules_dict

        self.field = self.__get_field(game_mode, height, width, rules_dict)

        self.game_mode = game_mode

        self.turn_count = 0
        self.winner = None
        self.turn_ongoing = False

        self.add_walkers(walker_dict, height, width)

        self.game_over_sfx_played = False

        self.whizz_mode = False

    def __get_field(self, game_mode: GameMode, height: int, width: int, rules_dict: dict) -> FieldType:

        if game_mode == GameMode.COINS:
            return CoinField([0, width, 0, height], self.music_manager, game_mode, rules_dict,
                             height, width)
        elif game_mode == GameMode.NORMAL:
            return InfiniteField([0, width, 0, height], self.music_manager, game_mode, rules_dict,
                                 height, width)
        elif game_mode == GameMode.SURVIVAL:
            return SurvivalField([0, width, 0, height], self.music_manager, game_mode, rules_dict,
                                 height, width)
        elif game_mode == GameMode.COPS:
            return CopsField([0, width, 0, height], self.music_manager, game_mode, rules_dict,
                             height, width)
        elif game_mode == GameMode.RACE:
            return RaceField([0, width, 0, height], self.music_manager, game_mode, rules_dict,
                             height, width)

    def add_walkers(self, walker_dict: dict, height: int, width: int) -> None:
        if 6 > len(walker_dict.keys()) > 0:
            for key in walker_dict.keys():
                walker = self.__generate_walker(walker_dict[key])
                if walker is not None:
                    self.field.add_walker(walker, self.game_mode, height, width)
        else:
            raise ValueError("Only 1 to 5 walkers Allowed!")

    def spawn_init_spaces(self, rules_dict: dict) -> None:
        self.field.spawn_init_spaces(rules_dict)

    def enact_turn(self) -> None:

        self.turn_count += 1
        self.field.init_moves()

    def step(self, screen):
        self.field.enact_single_step(screen, self.whizz_mode)

    def draw_all(self, screen):
        self.field.draw_all(screen)

    def toggle_offset(self):
        self.field.toggle_offset()

    def __generate_walker(self, data_list: list) -> [Walker, None]:
        if self.__valid_json_data_list(data_list):
            return Walker(data_list[0], data_list[1])
        return None

    def __valid_json_data_list(self, big_lst: list) -> bool:
        if len(big_lst) != 2:
            return False

        lst = big_lst[0]
        step_list_ok = (len(lst) == 2 and (isinstance(lst[0], float) or isinstance(lst[0], int)) and
                        (isinstance(lst[1], float) or isinstance(lst[1], int)))

        lst = big_lst[1]
        filter_list_ok = len(lst) == 2
        filter_list_ok = filter_list_ok and (isinstance(lst[0], float) or isinstance(lst[0], int))
        filter_list_ok = filter_list_ok and (isinstance(lst[1], float) or isinstance(lst[1], int))

        return step_list_ok and filter_list_ok

    def movement_ongoing(self):
        return self.field.turn_ongoing()

    def get_walkers(self) -> list:
        """
        Gets the list of all walkers
        :returns: a list of all walkers
        """
        return self.field.walkers

    def toggle_whizz_mode(self):
        self.whizz_mode = not self.whizz_mode


class InfiniteWalker(Game):

    def __init__(self, game_mode: GameMode, walker_dict: dict, rules_dict: dict, music: UIManager, screen_dim: tuple):
        super().__init__(game_mode, walker_dict, rules_dict, music, screen_dim)
        self.game_length = rules_dict["infinite_walker_length"]


    def game_over(self):
        return self.turn_count >= self.game_length


class Cops(Game):

    def __init__(self, walker_dict: dict, rules_dict: dict, music: UIManager, screen_dim: tuple):
        self.game_length = rules_dict["cops_game_length"]

        super().__init__(GameMode.COPS, walker_dict, rules_dict, music, screen_dim)

        self.field.copify(rules_dict["cop_robber_ratio"])
        self.__cops_win = False

    def game_over(self) -> bool:
        """
        checks if game should end according to game length and game mode
        :return: True if over, false if not
        """
        if self.turn_count >= self.game_length + 1:
            self.field.set_winners(False)
            self.__cops_win = False

            return True

        else:
            res = self.field.cops_win()
            if res:
                self.field.set_winners(True)
                self.__cops_win = True

            return res

    def get_cop_tup(self) -> tuple:
        """
        Return the cop_tup for gameScreen's get_final_data method.
        :return: If cops won, and the equivocal ratio
        """
        return (1 if self.__cops_win else 0), self.field.get_cop_ratio()


class Race(Game):
    def __init__(self, walker_dict: dict, rules_dict: dict, music: UIManager, screen_dim: tuple):
        super().__init__(GameMode.RACE, walker_dict, rules_dict, music, screen_dim)
        self.field.spawn_flag()

    def game_over(self):
        res = self.field.race_completed()
        if res is not False:
            losers = list(range(len(self.field.walkers)))
            if res in losers:
                losers.remove(res)

            self.field.set_winners([res], losers)

        return res is not False

    def get_screen_size(self) -> tuple:
        return 680, 680


class Coins(Game):
    def __init__(self, walker_dict: dict, rules_dict: dict, music: UIManager, screen_dim: tuple):
        super().__init__(GameMode.COINS, walker_dict, rules_dict, music, screen_dim)

        init_coin_num = rules_dict["init_coin_val"]
        self.field.add_coins(init_coin_num)

        self.__coin_add_interval = self.rules_dict["coin_add_interval"]
        self.__coins_per_interval = rules_dict["coins_per_interval"]

    def enact_turn(self) -> None:

        self.turn_count += 1
        self.field.init_moves()

        # add coins every 2 turns
        if self.turn_count % self.__coin_add_interval == 0:
            self.field.add_coins(self.__coins_per_interval)

    def game_over(self) -> bool:
        res = self.field.check_coin_win() != -1
        if res:
            losers = list(range(len(self.field.walkers)))
            losers.remove(res)

            self.field.set_winners([res], losers)
        return res


class Survival(Game):
    def __init__(self, walker_dict: dict, rules_dict: dict, music: UIManager, screen_dim: tuple):

        rules_dict["obstacle_num"] += 5

        super().__init__(GameMode.SURVIVAL, walker_dict, rules_dict, music, screen_dim)

        self.__add_interval = rules_dict["survival_add_interval"]
        self.__obsts_per_interval = rules_dict["obstacles_per_interval"]

    def enact_turn(self) -> None:

        self.turn_count += 1
        self.field.init_moves()

        # add coins every 2 turns
        if self.turn_count % self.__add_interval == 0:
            self.field.add_obsts(self.__obsts_per_interval)

    def game_over(self):
        res = self.field.check_survival_win()
        if res != -1:
            losers = list(range(len(self.field.walkers)))
            losers.remove(res)

            self.field.set_winners([res], losers)

        return res != -1


def get_game_object(game_mode: GameMode, walker_dict: dict, rules_dict: dict,
                    music: UIManager, screen_dim_tup: tuple) -> Game:
    if game_mode == GameMode.COPS:
        return Cops(walker_dict, rules_dict, music, screen_dim_tup)
    elif game_mode == GameMode.RACE:
        return Race(walker_dict, rules_dict, music, screen_dim_tup)
    elif game_mode == GameMode.COINS:
        return Coins(walker_dict, rules_dict, music, screen_dim_tup)
    elif game_mode == GameMode.SURVIVAL:
        return Survival(walker_dict, rules_dict, music, screen_dim_tup)

    return InfiniteWalker(GameMode.NORMAL, walker_dict, rules_dict, music, screen_dim_tup)