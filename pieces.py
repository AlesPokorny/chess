import tkinter as tk
from typing import List

from PIL import ImageTk

import config
from utils import calculate_canvas_coordinates_from_board


class Piece:
    def __init__(self, piece: str, pos: list, canvas: tk.Canvas):
        piece_type = piece[0]
        if piece_type in config.PIECE_TYPES:
            self.piece = piece_type
        else:
            raise ValueError("Piece doesn't exist, you lemon")

        self.canvas = canvas
        self.is_white = self.piece.isupper()
        self.pos = pos
        self.image = self.get_piece_image()
        self.drawn_image = None
        self.same_color_piece_pos = []
        self.opponent_piece_pos = []
        self.possible_moves = []

    def get_piece_image(self):
        if self.is_white:
            color = "w"
        else:
            color = "b"

        piece_type = self.piece.lower()
        image_name = f"{piece_type}{color}.png"
        image_path = f"./resources/{image_name}"
        try:
            img = ImageTk.PhotoImage(file=image_path)
        except OSError:
            raise OSError(f"Missing piece picture for {image_name}")
        return img

    def draw_piece(self):
        canvas_x, canvas_y = calculate_canvas_coordinates_from_board(self.pos[0], self.pos[1])
        self.drawn_image = self.canvas.create_image(canvas_x, canvas_y, anchor="nw", image=self.image)

    def move_piece(self, move_x, move_y):
        self.canvas.move(self.drawn_image, move_x, move_y)

    def calculate_possible_moves(self, pieces_pos: list) -> list:
        self.split_piece_pos_color(pieces_pos=pieces_pos)
        piece_type = self.piece.lower()
        if piece_type == "n":
            moves = self.get_knight_moves()
        elif piece_type == "k":
            moves = self.get_king_moves()
        elif piece_type == "b":
            moves = self.get_bishop_moves()
        elif piece_type == "p":
            moves = self.get_pawn_moves()
        elif piece_type == "r":
            moves = self.get_rook_moves()
        elif piece_type == "q":
            moves = self.get_queen_moves()
        else:
            moves = []

        moves = self.filter_off_the_board_moves(moves=moves)

        self.possible_moves = moves

    def get_rook_moves(self) -> List:
        x, y = self.pos
        max_step = max([x, y, 7 - x, 7 - y])

        directions = [
            [0, 1],
            [0, -1],
            [-1, 0],
            [1, 0],
        ]

        allowed_moves = self.get_straight_moves(directions=directions, max_step=max_step)

        return allowed_moves

    def get_queen_moves(self) -> List:
        x, y = self.pos
        max_step = max([x, y, 7 - x, 7 - y])

        directions = [
            [0, 1],
            [0, -1],
            [-1, 0],
            [1, 0],
            [1, 1],
            [1, -1],
            [-1, 1],
            [-1, -1],
        ]

        allowed_moves = self.get_straight_moves(directions=directions, max_step=max_step)

        return allowed_moves

    def get_knight_moves(self) -> list:
        x, y = self.pos
        move_distances = [
            [-2, -1],
            [-2, 1],
            [2, -1],
            [2, 1],
            [-1, -2],
            [1, -2],
            [-1, 2],
            [1, 2],
        ]

        moves = []
        for move_x, move_y in move_distances:
            new_x = x + move_x
            new_y = y + move_y
            moves.append([new_x, new_y])

        allowed_moves = []
        for pos in moves:
            if pos not in self.same_color_piece_pos:
                allowed_moves.append(pos)

        return allowed_moves

    def get_king_moves(self) -> list:
        x, y = self.pos
        moves = [
            [x, y + 1],
            [x, y - 1],
            [x + 1, y],
            [x - 1, y],
            [x + 1, y + 1],
            [x + 1, y - 1],
            [x - 1, y + 1],
            [x - 1, y - 1],
        ]

        allowed_moves = []
        for pos in moves:
            if pos not in self.same_color_piece_pos:
                allowed_moves.append(pos)

        return allowed_moves

    def get_bishop_moves(self) -> list:
        x, y = self.pos
        max_step = max([x, y, 7 - x, 7 - y])

        directions = [
            [1, 1],
            [1, -1],
            [-1, 1],
            [-1, -1],
        ]

        allowed_moves = self.get_straight_moves(directions=directions, max_step=max_step)

        return allowed_moves

    def get_pawn_moves(self) -> list:
        # TODO: Add en passant
        # TODO: Add promotion
        x, y = self.pos
        forward_moves = []
        if self.is_white:
            direction = -1
            starting_y = 6
        else:
            direction = 1
            starting_y = 1

        if y == starting_y:
            forward_moves.append([x, y + 2 * direction])

        forward_moves.append([x, y + direction])
        allowed_moves = []
        for pos in forward_moves:
            if (pos not in self.same_color_piece_pos) and (pos not in self.opponent_piece_pos):
                allowed_moves.append(pos)

        capture_moves = [[x - 1, y + direction], [x + 1, y + direction]]

        for pos in capture_moves:
            if pos in self.opponent_piece_pos:
                allowed_moves.append(pos)

        return allowed_moves

    def split_piece_pos_color(self, pieces_pos: list):
        same_color_pieces = list(
            filter(
                lambda piece: piece[0].islower() == self.piece.islower(),
                pieces_pos,
            )
        )
        self.same_color_piece_pos = [pieces_pos[piece] for piece in same_color_pieces]
        self.opponent_piece_pos = [pieces_pos[piece] for piece in pieces_pos if piece not in same_color_pieces]

    @staticmethod
    def filter_off_the_board_moves(moves: List[List]) -> List:
        allowed_moves = []
        for x, y in moves:
            if 0 <= x < 8 and 0 <= y < 8:
                allowed_moves.append([x, y])

        return allowed_moves

    def get_pos_from_direction(self, dx: int, dy: int) -> List:
        x, y = self.pos

        return [x + dx, y + dy]

    def get_straight_moves(self, directions: List, max_step: int) -> List:
        allowed_moves = []

        for direction in directions:
            for step in range(1, max_step + 2):
                dx, dy = [value * step for value in direction]

                output_pos = self.get_pos_from_direction(dx=dx, dy=dy)

                if output_pos[0] > 7 or output_pos[1] > 7:
                    break
                elif output_pos in self.opponent_piece_pos:
                    allowed_moves.append(output_pos)
                    break
                elif output_pos in self.same_color_piece_pos:
                    break
                else:
                    allowed_moves.append(output_pos)

        return allowed_moves
