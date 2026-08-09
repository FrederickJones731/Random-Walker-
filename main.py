import argparse

import pygame

from game_screen import *
from title_screen import *
from graph_screen import *
from game import *

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 680

HELP_DESCRIPTION = ("Random Walker DX:\n"
                    "This program simulates a walker, walking and endless 2d space, or many minigames."
                    "\nThere are 5 Game modes:\n  - Infinite Walker: Walk forever."
                    "\n  - Coin Runners: Get as many coins as you can!"
                    "\n  - Cops n' Robbers: Some walkers are counted as cops. Catch those dang robbers!"
                    "\n  - Survival: Don't hit the expanding fire! Last survivor wins!"
                    "\n  - Race: Get to the end goal as fast as you can!\n\n"
                    "Use the mouse to interact with the buttons on screen.\n"
                    "Press the Space Bar in order to speed up the simulation.\n"
                    "Press the 'w' key during a game to enter Whizz Mode! Zoom through a simulation, "
                    "at the cost of visuals!"
                    "Press 'Backspace' To exit early, and return to the main screen. "
                    "This is also used to end an ongoing game.\n"
                    "Press the 'm' key to Mute the Music.\n"
                    "Press the 'n' key to Mute all SFX.")


def main_screen_procedure(mouse_pos, mouse_click: bool) -> bool:
    """
    Checks if any button is being clicked, and once one is, go to the appropriate activity
    :return: True or false, to reset check_ongoing once a game starts
    """
    menu_screen.screen.fill((255, 255, 255))
    menu_screen.show_all_main_buttons()

    game_mode = menu_screen.get_button_clicked_location(mouse_pos, mouse_click)
    if game_mode is None:
        # Nothing was clicked
        return True

    elif game_mode is GameMode.GRAPHS:
        # for graphs screen only
        music_man.play_button_click()
        graph_screen.make_cur_screen(GameMode.GRAPHS, music_man, False)
        menu_screen.end_current_screen()
        return False

    else:
        # any one of the game buttons
        music_man.play_button_click()
        game_screen.make_cur_screen(game_mode, music_man)
        menu_screen.end_current_screen()

        return True


def game_screen_procedure(ongoing: bool) -> bool:
    """
    Enacts the game procedure, to be run from main loop.
    Returns true if the game should continue going.
    :param ongoing: If the game is still ongoing.
    :return: True if the game should keep on going, False otherwise
    """

    tup = game_screen.game_screen_procedure(ongoing)

    if tup[1]:
        # if the game ended, sfx played.
        # return immediately to main screen.
        back_to_main_screen(game_screen)

    # if game should keep on going
    return tup[0]


def back_to_main_screen(screen: Screen) -> None:
    """
    Returns from the selected screen back to main screen
    :param screen: Either gameScreen or GraphScreen.
    :return: Nothing
    """

    menu_screen.make_cur_screen(GameMode.MAIN_SCREEN, music_man, screen is not graph_screen)
    screen.end_current_screen()


def graph_screen_procedure(mouse_pos, mouse_click: bool) -> None:
    """
    What should run every loop when the graph screen is up.
    :return: Nothing
    """
    graph_screen.show_all_graph_views()

    plot_clicked = graph_screen.get_clicked_button(mouse_pos, mouse_click)
    if plot_clicked is not None:
        # a button has been clicked. Swap plot view
        graph_screen.make_new_plot(plot_clicked)
        music_man.play_button_click()


def main() -> None:
    """
    The main, pygame cycle of events.
    The main function in charge of the entire program is here.
    :return: None
    """
    done = False
    check_ongoing = True

    while not done:

        # gets mouse position, and if it being clicked
        mouse_pos = py.mouse.get_pos()
        mouse_click = py.mouse.get_pressed()[0]

        if menu_screen.is_active():
            check_ongoing = main_screen_procedure(mouse_pos, mouse_click)

        elif game_screen.is_active():
            check_ongoing = game_screen_procedure(check_ongoing)

        elif graph_screen.is_active():
            graph_screen_procedure(mouse_pos, mouse_click)

        for event in py.event.get():
            if event.type == py.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_m:
                    music_man.toggle_music()

                if event.key == pygame.K_n:
                    music_man.toggle_sfx()

                if game_screen.is_active():
                    if event.key == pygame.K_SPACE:
                        game_screen.game.toggle_offset()
                    if event.key == pygame.K_BACKSPACE:
                        check_ongoing = False
                    if event.key == pygame.K_w:
                        game_screen.toggle_whizz_mode()

                if graph_screen.is_active():
                    if event.key == pygame.K_BACKSPACE:
                        check_ongoing = False
                        music_man.play_button_click()
                        back_to_main_screen(graph_screen)

        py.display.flip()


if __name__ == "__main__":

    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description=HELP_DESCRIPTION)

    parser.add_argument('--text', type=str, help='Random Walker DX - Begin!')

    args = parser.parse_args()

    if args.text:
        # Print the provided text
        print(args.text)

    music_man = UIManager()

    py.init()
    py.font.init()

    data_dict = {
        GraphType.X_AXIS_CROSSED: [],
        GraphType.Y_AXIS_CROSSED: [],
        GraphType.PERIMETER_DIST: [],
        GraphType.SPAWN_DIST: [],
        GraphType.PORTALS_USED: [],
        GraphType.OBSTACLES_HIT: [],
        GraphType.COINS_PER_TURN: [],
        GraphType.COIN_GAME_LENGTH: [],
        GraphType.COPS_WIN_PERCENT: [],
        GraphType.RACE_GAME_LENGTH: [],
        GraphType.SURVIVAL_GAME_LENGTH: []
    }

    menu_screen = TitleScreen(SCREEN_WIDTH, SCREEN_HEIGHT, music_man)
    game_screen = GameScreen(SCREEN_WIDTH, SCREEN_HEIGHT, music_man, data_dict)
    graph_screen = GraphScreen(SCREEN_WIDTH, SCREEN_HEIGHT, music_man, data_dict)

    py.display.set_caption("Random Walker DX")

    menu_screen.make_cur_screen(GameMode.MAIN_SCREEN, music_man)

    main()

    py.quit()
