import pygame.image
from matplotlib.backends.backend_template import FigureCanvas
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from button import *
from enums import *
import matplotlib.pyplot as plt

TEXT_COLOR = (122, 122, 122)

button_texts = [
    "Perimeter Cross",
    "X Axis Crossed",
    "Y Axis Crossed",
    "Distance From Spawn",
    "Obstacles Hit (Per Game)",
    "Portals Used (Per Game)",
    "Coin Game Length",
    "Coins Per Turn",
    "Cops Win Percent",
    "Survival Game Length",
    "Race Game Length"
]

PERIMETER_DIST = 50
SAVE_BUTTON_DIMS = (80, 80)

# GraphType: [title, X_axis_txt, Y_axis_txt]
graph_index_dict = {
    GraphType.PERIMETER_DIST: [f"Turn count to get {PERIMETER_DIST} spaces from Spawn:", "Turns", "Frequency"],
    GraphType.X_AXIS_CROSSED: ["Number of Times X Axis Was Crossed:", "# of Times", "Frequency"],
    GraphType.Y_AXIS_CROSSED: ["Number of Times Y Axis Was Crossed:", "# of Times", "Frequency"],
    GraphType.SPAWN_DIST: ["Average Distance From Spawn:", "Turns", "Distance"],
    GraphType.OBSTACLES_HIT: ["Number of Obstacles Hit (Per Game):", "Obstacles Hit", "Frequency"],
    GraphType.PORTALS_USED: ["Number of Portals Used (Per Game):", "Portals Used", "Frequency"],
    GraphType.COIN_GAME_LENGTH: ["Average Length of a Coins Game:", "Turn Count", "Frequency"],
    GraphType.COINS_PER_TURN: ["Coins Acquired Per Turn:", "Coin Amount", "Frequency"],
    GraphType.COPS_WIN_PERCENT: ["Cops Win Percent:", "Cops/Robber Percentage", "Win Percent"],
    GraphType.SURVIVAL_GAME_LENGTH: ["Average Length of a Survival Game:", "Turn Count", "Frequency"],
    GraphType.RACE_GAME_LENGTH: ["Average Length of a Race Game:", "Turn Count", "Frequency"],
}


class GraphScreen(Screen):
    def __init__(self, width: float, height: float, music: UIManager, data_dict: dict):
        super().__init__(int(width), int(height), music)

        self.data_dict = data_dict

        button_height = height / len(button_texts)
        cur_height = 0

        self.buttons = []
        enums = [enum for enum in GraphType]
        i = 0

        for text in button_texts:
            button = Button(enums[i], 0, cur_height, 250, button_height - 5, TEXT_COLOR, text, 16)
            self.buttons.append(button)
            cur_height += button_height
            i += 1

        save_button_image = pygame.transform.scale(pygame.image.load("anims/save_icon.png"), SAVE_BUTTON_DIMS)
        save_b_x, save_b_y = width - SAVE_BUTTON_DIMS[0] - 20, height - SAVE_BUTTON_DIMS[1] - 20

        self.__show_save_button = False
        self.__save_button = ImageButton(GameMode.GRAPHS, save_b_x, save_b_y, SAVE_BUTTON_DIMS[0], SAVE_BUTTON_DIMS[1],
                                         TEXT_COLOR, save_button_image)

        self.__cur_plot = None
        self.__cur_fig = None
        self.__cur_graph_name = None

        # initial value
        # self.make_new_plot(GraphType.PERIMETER_DIST)

    def show_all_graph_views(self):

        self.screen.blit(self.background, (0, 0))

        for button in self.buttons:
            button.show(self.screen)

        if self.__cur_plot is not None:
            self.screen.blit(self.__cur_plot, (400, 100))

        if self.__show_save_button:
            self.__save_button.show(self.screen)

    def get_clicked_button(self, mouse_pos, mouse_clicked) -> [Enum, None]:
        """
        Returns the graph type of the button being pressed.
        :param mouse_pos: Mouse's current position
        :param mouse_clicked: If the left mouse key is being pressed or not
        :return: The GraphType of the button being pressed, None otherwise.
        """
        for button in self.buttons:
            if button.is_being_clicked(mouse_pos, mouse_clicked):
                return button.get_link()
        if self.__show_save_button and self.__save_button.is_being_clicked(mouse_pos, mouse_clicked):
            # save procedure
            name = self.__cur_graph_name.name + ".png"
            self.music.play_button_click()
            plt.savefig(name)

        return None

    def make_new_plot(self, graph: GraphType) -> None:

        self.__show_save_button = True

        if self.__cur_fig is not None:
            plt.close(self.__cur_fig)

        x, y = self.__get_plot_vals(graph)

        # Add labels and title
        labels = graph_index_dict[graph]

        # Render the Matplotlib plot onto a Pygame surface
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel(labels[1])
        ax.set_ylabel(labels[2])
        ax.set_title(labels[0])

        plt.xticks(self.trim_ticks(x))
        plt.yticks(self.trim_ticks(y))

        canvas = FigureCanvas(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()

        self.__cur_plot = pygame.image.fromstring(raw_data, size, "RGB")
        self.__cur_fig = fig
        self.__cur_graph_name = graph

    def __get_plot_vals(self, graph_type: GraphType) -> tuple:
        avg_list = [GraphType.SPAWN_DIST, GraphType.COPS_WIN_PERCENT]

        if graph_type not in avg_list:
            return self.__compile_plot_lists(self.data_dict[graph_type], True)
        else:
            return self.__compile_plot_lists(self.data_dict[graph_type], False)

    def trim_ticks(self, lst: list) -> list:
        """
        Trim ticks so it doesnt overload
        :param lst: list to trim
        :return: trimmed list
        """
        while len(lst) / 2 > 8:
            lst = lst[::2]

        return lst

    def __compile_plot_lists(self, comp_list: list, calc_sum: bool) -> tuple:
        """
        Makes plot lists to be shown in the graphs
        :param comp_list: List to decypher
        :param calc_sum: True if it should calculate sum of all the times each condition was met.
                        otherwise, calcs the average of each time the condition occurred
        :return: a list for x_values, a list for y_values
        """

        comp_dict = {0: 0, 1: 0}

        if calc_sum:
            for game_list in comp_list:
                if not isinstance(game_list, int):
                    for item in game_list:
                        if isinstance(item, list) or isinstance(item, tuple):
                            if item[0] in comp_dict:
                                comp_dict[item[0]] += 1
                            else:
                                comp_dict[item[0]] = 1
                        elif isinstance(item, int) or isinstance(item, float):
                            if item in comp_dict:
                                comp_dict[item] += 1
                            else:
                                comp_dict[item] = 1

        # calculate average
        else:
            for game_list in comp_list:
                # for cop_tuples. (0/1 for lose/win, cop-ratio)
                if isinstance(game_list, tuple):
                    if game_list[1] in comp_dict:
                        comp_dict[game_list[1]] += game_list[0], 1
                    else:
                        comp_dict[game_list[1]] = game_list[0], 1

                # for longer lists - calculate
                elif isinstance(game_list, list):
                    turn_count = 1
                    for avg_val in game_list:
                        if turn_count in comp_dict and not isinstance(comp_dict[turn_count], int):
                            temp_avg = comp_dict[turn_count][0] + avg_val
                            temp_div = comp_dict[turn_count][1] + 1
                            comp_dict[turn_count] = temp_avg, temp_div
                        else:
                            comp_dict[turn_count] = avg_val, 1
                        turn_count += 1

            for key in comp_dict.keys():
                tup = comp_dict[key]
                if isinstance(tup, tuple) and tup[1] != 0:
                    comp_dict[key] = tup[0] / tup[1]

        sorted_key_list = sorted(comp_dict.keys())
        return sorted_key_list, [comp_dict[key] for key in sorted_key_list]
