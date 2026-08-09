from button import *
from game import *


PERIMETER_DIST = 50

GameType = [Game, Coins, Cops, Survival, InfiniteWalker, Race]


class Tracker:
    def __init__(self, game: GameType):
        self.walker_pos_list = []
        self.game = game

    def get_final_data(self, data_dict: dict, walkers: list, game_mode: GameMode,
                       game_length: int, cop_game_tup: tuple = None) -> None:
        """
        Formats all the data from this game, to be read on later in the graph activity.
        :param data_dict: The dictionary to store all data in
        :param walkers: A list of all the walkers (post game)
        :param game_mode: Game mode of elapsed game
        :param game_length: Number of turn
        :param cop_game_tup: A tuple received from after a cop game. (cops_win: bool, cop_ratio: float)
        :return: nothing. Just updates the dict
        """

        self.__set_walker_pos_list(walkers)

        data_dict[GraphType.X_AXIS_CROSSED].append(self.calc_axis_cross(True))
        data_dict[GraphType.Y_AXIS_CROSSED].append(self.calc_axis_cross(False))

        data_dict[GraphType.PERIMETER_DIST].append(self.get_perimeter_list())
        data_dict[GraphType.SPAWN_DIST].append(self.__get_spawn_dist_list())

        data_dict[GraphType.PORTALS_USED].append(self.__get_portals_used_list(walkers))
        data_dict[GraphType.OBSTACLES_HIT].append(self.__get_obstacles_hit_list(walkers))

        if game_mode == GameMode.COINS:
            data_dict[GraphType.COINS_PER_TURN] = self.__get_coins_per_turn_list(walkers, game_length)
            data_dict[GraphType.COIN_GAME_LENGTH].append([game_length])

        elif game_mode == GameMode.COPS:
            data_dict[GraphType.COPS_WIN_PERCENT].append(cop_game_tup)

        elif game_mode == GameMode.RACE:
            data_dict[GraphType.RACE_GAME_LENGTH].append([game_length])

        elif game_mode == GameMode.SURVIVAL:
            data_dict[GraphType.SURVIVAL_GAME_LENGTH].append([game_length])

    def __calc_spawn_dist(self, position: tuple, spawn_pos: tuple) -> float:
        """
        returns the raw distance from the starting point using the coords given. simple pythagoras
        :param position: current postion coordinates
        :return: float value, signifying the distance from spawn
        """
        x_val = abs(position[0] - spawn_pos[0])
        y_val = abs(position[1] - spawn_pos[1])
        base = x_val**2 + y_val**2
        return math.sqrt(base)

    def get_perimeter_list(self):
        """
        Checks when the first time the walker exited set perimeter.
        :return: A list, one position for each walker. Which turn it took to leave perimeter
        """
        perimeter_cross_list = []

        for walker in self.walker_pos_list:
            for pos in range(len(walker)):
                if self.__calc_spawn_dist(walker[pos], walker[0]) >= PERIMETER_DIST:
                    perimeter_cross_list.append(pos)
                    break
            else:
                perimeter_cross_list.append(-1)

        return perimeter_cross_list

    def calc_axis_cross(self, calc_x_axis: bool) -> list:

        axis_cross_list = []

        for walker in self.walker_pos_list:
            prev_val, count = 0, 0

            for pos in walker:

                cur_pos_val = pos[1]
                if calc_x_axis:
                    cur_pos_val = pos[0]

                spawn_loc = walker[0][0] if calc_x_axis else walker[0][1]
                if (prev_val < spawn_loc <= cur_pos_val) or (prev_val > spawn_loc >= cur_pos_val):
                    # cross has occured
                    count += 1

                prev_val = cur_pos_val

            tup = count, len(walker)
            axis_cross_list.append(tup)

        return axis_cross_list

    def __get_spawn_dist_list(self) -> list:
        """
        makes a list for each walker, calculating distance from spawn each turn.
        :return: list of lists - each with distance at each interval
        """
        perimeter_dist_list = []
        index = 0

        # list for each walker - each one has that turns dist. from spawn point
        for walker_data in self.walker_pos_list:
            if len(walker_data) > 0:
                spawn_pos = walker_data[0]
                perimeter_dist_list.append([])

                # per space in walker_data
                for pos_id in range(len(walker_data)):
                    position = walker_data[pos_id]
                    perimeter_dist_list[index].append(self.__calc_spawn_dist(position, spawn_pos))

                index += 1
            else:
                perimeter_dist_list.append([0.0])

        # compile all data into one list
        new_lst = []
        cur = 0
        while True:
            count, summ = 0, 0
            for i in range(len(perimeter_dist_list)):
                if len(perimeter_dist_list[i]) > cur:
                    count += 1
                    summ += perimeter_dist_list[i][cur]

            if count == 0:
                break
            else:
                new_lst.append(summ // count)
                cur += 1

        return new_lst

    def __get_portals_used_list(self, walkers: list) -> list:
        portals_used_lst = []
        for walker in walkers:
            portals_used_lst.append(walker.get_portals_used_count())
        return portals_used_lst

    def __get_obstacles_hit_list(self, walkers: list) -> list:
        obsts_hit_lst = []
        for walker in walkers:
            obsts_hit_lst.append(walker.get_obstacles_hit_count())
        return obsts_hit_lst

    def __get_coins_per_turn_list(self, walkers: list, game_length: int) -> list:
        """
        Calculates average coins gotten per turn.
        :param walkers: A list of all the game's walkers (post game)
        :param game_length: turn elapsed
        :return: a list, each position an avg of coins received per turn per walker
        """

        avg_list = []
        for walker in walkers:
            avg = walker.get_coin_val() / game_length
            avg_list.append([self.__round_to_closest(avg)])

        return avg_list

    def __round_to_closest(self, avg: float) -> float:
        return round(avg*20) / 20

    def __set_walker_pos_list(self, walkers: list) -> None:
        """
        Set the class' walker position list.
        :return: Nothing
        """
        for walker in walkers:
            self.walker_pos_list.append(walker.get_final_loc_list())


class GameScreen(Screen):

    def __init__(self, width: int, height: int, music: UIManager, data_dict: dict):
        super().__init__(width, height, music)

        self.game = None

        self.data_dict = data_dict
        self.tracker = Tracker(self.game)

        self.__whizz_mode = False

    def game_screen_procedure(self, ongoing: bool) -> tuple:
        """
        Does each game iteration tick. Returns if the game should keep on going.
        :param ongoing: if the game is still currently running
        :return: If the game should keep on going, and
            kill-screen: if should exit this screen immediately and go back to main
        """
        kill_screen = False

        self.screen.fill((255, 255, 255))
        if not self.__whizz_mode or not ongoing:
            # while whizz mode is on, and game isnt over...
            self.screen.blit(self.background, (0, 0))

        if ongoing:
            if self.game.movement_ongoing():
                # step forward until all walkers have walked
                self.game.step(self.screen)
                return not self.game.game_over(), False
            else:
                # randomize values for each walker
                self.game.enact_turn()
                return True, False
        else:
            # game is over. enact exit sequence
            self.game.draw_all(self.screen)
            self.game.music_manager.end_music()

            self.__whizz_mode = False

            if not self.game.game_over_sfx_played:
                # did the game over sound play?
                self.music.play_game_over_sfx()
                self.game.game_over_sfx_played = True

            if not py.mixer.get_busy():
                # sfx is up. return to main
                self.update_dict()
                kill_screen = True

        return False, kill_screen

    def update_dict(self) -> None:
        """
        updates dictionary data, for research purposes. kills game
        :return: None
        """
        cop_tup = None
        if self.game_mode == GameMode.COPS:
            cop_tup = self.game.get_cop_tup()
        self.tracker.get_final_data(self.data_dict, self.game.get_walkers(),
                                    self.game.game_mode, self.game.turn_count, cop_tup)

        self.game = None

    def toggle_whizz_mode(self):
        self.game.toggle_whizz_mode()
        self.__whizz_mode = not self.__whizz_mode
