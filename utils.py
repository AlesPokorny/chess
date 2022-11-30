import math
import config


def calculate_board_coordinates_from_canvas(x: int, y: int) -> (int, int):
    coordinate_offset = config.SQUARE_SIZE / 2
    board_x = math.floor(x / config.SQUARE_SIZE)
    board_y = math.floor(y / config.SQUARE_SIZE)
    x = board_x * config.SQUARE_SIZE + coordinate_offset
    y = board_y * config.SQUARE_SIZE + coordinate_offset
    return board_x, board_y, x, y


def calculate_canvas_coordinates_from_board(x: int, y: int) -> (int, int):
    canvas_x = x * config.SQUARE_SIZE
    canvas_y = y * config.SQUARE_SIZE
    return canvas_x, canvas_y
