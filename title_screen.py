from button import *

TEXT_COLOR = (122, 122, 122)


class TitleScreen(Screen):

    def __init__(self, width: int, height: int, music: UIManager):
        # main screen buttons
        super().__init__(width, height, music)

        self.music = music
        self.__button_sfx_played = False

        self.title = TextBox(370, 80, 500, 100, TEXT_COLOR, "Random Walker DX", 40)

        self.normal_button = Button(GameMode.NORMAL, 125, 350, 220, 80, TEXT_COLOR, "Normal")
        self.race_button = Button(GameMode.RACE, 125, 550, 220, 80, TEXT_COLOR, "Race")
        self.coin_button = Button(GameMode.COINS, 515, 350, 220, 80, TEXT_COLOR, "Coin Runners")
        self.cops_button = Button(GameMode.COPS, 900, 350, 220, 80, TEXT_COLOR, "Cops n' Robbers")
        self.survival_button = Button(GameMode.SURVIVAL, 515, 550, 220, 80, TEXT_COLOR, "Survival")
        self.graph_button = Button(GameMode.GRAPHS, 900, 550, 220, 80, TEXT_COLOR, "Graphs!")

    def show_all_main_buttons(self):
        self.screen.blit(self.background, (0, 0))

        self.title.show(self.screen)

        self.normal_button.show(self.screen)
        self.race_button.show(self.screen)
        self.cops_button.show(self.screen)
        self.coin_button.show(self.screen)
        self.survival_button.show(self.screen)
        self.graph_button.show(self.screen)


    def get_button_sfx_played(self):
        if not self.__button_sfx_played:
            self.__button_sfx_played = True
            return False
        return True

    def get_button_clicked_location(self, mouse_pos, mouse_click):

        if self.normal_button.is_being_clicked(mouse_pos, mouse_click):
            return GameMode.NORMAL

        elif self.race_button.is_being_clicked(mouse_pos, mouse_click):
            return GameMode.RACE

        elif self.coin_button.is_being_clicked(mouse_pos, mouse_click):
            return GameMode.COINS

        elif self.cops_button.is_being_clicked(mouse_pos, mouse_click):
            return GameMode.COPS

        elif self.survival_button.is_being_clicked(mouse_pos, mouse_click):
            return GameMode.SURVIVAL

        elif self.graph_button.is_being_clicked(mouse_pos, mouse_click):
            return GameMode.GRAPHS
