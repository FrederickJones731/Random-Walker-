from enum import Enum


Step = [float, float]


class GameMode(Enum):
    NORMAL = 0
    RACE = 1
    COPS = 2
    COINS = 3
    SURVIVAL = 4
    MAIN_SCREEN = 5
    GRAPHS = 6


class GraphType(Enum):
    PERIMETER_DIST = 0
    X_AXIS_CROSSED = 1
    Y_AXIS_CROSSED = 2
    SPAWN_DIST = 3
    OBSTACLES_HIT = 5
    PORTALS_USED = 6
    COIN_GAME_LENGTH = 7
    COINS_PER_TURN = 8
    COPS_WIN_PERCENT = 9
    SURVIVAL_GAME_LENGTH = 10
    RACE_GAME_LENGTH = 11