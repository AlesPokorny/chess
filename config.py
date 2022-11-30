import numpy as np

PIECE_TYPES = ["p", "r", "n", "b", "q", "k", "P", "R", "N", "B", "Q", "K"]
PIECES = {
    "r0": [0, 0],
    "n0": [1, 0],
    "b0": [2, 0],
    "q0": [3, 0],
    "k0": [4, 0],
    "b1": [5, 0],
    "n1": [6, 0],
    "r1": [7, 0],
    "p0": [0, 1],
    "p1": [1, 1],
    "p2": [2, 1],
    "p3": [3, 1],
    "p4": [4, 1],
    "p5": [5, 1],
    "p6": [6, 1],
    "p7": [7, 1],
    "R0": [0, 7],
    "N0": [1, 7],
    "B0": [2, 7],
    "Q0": [3, 7],
    "K0": [4, 7],
    "B1": [5, 7],
    "N1": [6, 7],
    "R1": [7, 7],
    "P0": [0, 6],
    "P1": [1, 6],
    "P2": [2, 6],
    "P3": [3, 6],
    "P4": [4, 6],
    "P5": [5, 6],
    "P6": [6, 6],
    "P7": [7, 6],
}

STARTING_POSITION = np.array(
    [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        ["R", "N", "B", "Q", "K", "B", "N", "R"],
    ]
)

SQUARE_SIZE = 64
BOARD_SIZE = SQUARE_SIZE * 8

WHITE_SQUARE_COLOR = "#ec8883"
DARK_SQUARE_COLOR = "#ae3219"
SELECT_COLOR = "green"
SELECT_WIDTH = 2
MOVE_MARK_COLOR = "#7770d2"
MOVE_MARK_SIZE_OFFSET = 5

GAME_TITLE = "Chess"
