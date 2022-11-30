import numpy as np
import config
import constants
from pieces import Piece
import tkinter as tk
from utils import (
    calculate_board_coordinates_from_canvas,
    calculate_canvas_coordinates_from_board,
)
from typing import List, Type
import subprocess


class Chess:
    def __init__(self):
        self.tk_root = tk.Tk()
        self.tk_root.title(config.GAME_TITLE)
        self.canvas = tk.Canvas(height=config.BOARD_SIZE, width=config.BOARD_SIZE)
        self.selected_item = {
            "item": Type[int],
            "board_xy": [Type[int], Type[int]],
            "canvas_xy": [Type[int], Type[int]],
            "piece": Type[str],
            "item_turn": False,
        }
        self.is_selected = False
        self.board = np.ndarray(shape=(8, 8), dtype=Piece)
        self.pieces = {}
        self.pieces_pos = config.PIECES
        self.select_rect = None
        self.white_turn = True
        self.is_player_turn = True
        self.possible_moves = []
        self.possible_move_mark = []
        self.selected_coordinates = {
            "board_x": Type[int],
            "board_y": Type[int],
            "canvas_x": Type[int],
            "canvas_y": Type[int],
        }

    def run(self):
        self.init_pieces()
        self.draw_board()
        self.draw_pieces()
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

    def init_pieces(self):
        for piece, pos in self.pieces_pos.items():
            self.pieces[piece] = Piece(piece=piece, canvas=self.canvas, pos=pos)

    def draw_board(self):
        for row_number, row in enumerate(self.board):
            x = config.SQUARE_SIZE * row_number
            for column_number, piece in enumerate(row):
                if (row_number + column_number) % 2 == 0:
                    fill = config.WHITE_SQUARE_COLOR
                else:
                    fill = config.DARK_SQUARE_COLOR

                y = config.SQUARE_SIZE * column_number

                self.canvas.create_rectangle(
                    x,
                    y,
                    x + config.SQUARE_SIZE,
                    y + config.SQUARE_SIZE,
                    fill=fill,
                    outline=fill,
                )

    def draw_pieces(self):
        for _, piece in self.pieces.items():
            piece.draw_piece()

    def on_click(self, event):
        self.canvas.delete(self.select_rect)
        (
            self.selected_coordinates["board_x"],
            self.selected_coordinates["board_y"],
            self.selected_coordinates["canvas_x"],
            self.selected_coordinates["canvas_y"],
        ) = calculate_board_coordinates_from_canvas(event.x, event.y)
        self.remove_possible_move_marks()
        piece_name = self.get_piece_from_position()

        print("\n\n")
        print("Clicked on:")
        print(f"Piece {piece_name}:")
        print(f"White turn {self.white_turn}")
        print(f'board coordinates {self.selected_coordinates["board_x"], self.selected_coordinates["board_y"]}')
        if (
            self.is_selected & self.selected_item["item_turn"]
            and len(self.possible_moves) > 0
        ):
            if [self.selected_coordinates["board_x"], self.selected_coordinates["board_y"]] in self.possible_moves:
                if piece_name:
                    self.move_with_capture()
                else:
                    self.move_piece()
            else:
                self.select_piece(piece_name=piece_name)
                self.get_possible_moves(piece_name)
        else:
            if piece_name:
                self.select_piece(piece_name=piece_name)
                self.get_possible_moves(piece_name)
            else:
                self.create_select_rectangle()
                self.is_selected = False

    def get_possible_moves(self, piece_name):
        if self.selected_item["item_turn"]:
            self.pieces[piece_name].calculate_possible_moves(pieces_pos=self.pieces_pos)
            self.possible_moves = self.pieces[piece_name].possible_moves
            print(f"Possible moves: {self.possible_moves}")
            self.draw_possible_moves()

    def remove_possible_move_marks(self):
        if len(self.possible_move_mark):
            for mark_to_delete in self.possible_move_mark:
                self.canvas.delete(mark_to_delete)
            self.possible_move_mark = []

    def draw_possible_moves(self):
        if len(self.possible_moves) > 0:
            for x, y in self.possible_moves:
                circle_x, circle_y = calculate_canvas_coordinates_from_board(x, y)
                circle_x = circle_x + config.SQUARE_SIZE / 2
                circle_y = circle_y + config.SQUARE_SIZE / 2
                self.possible_move_mark.append(
                    [
                        self.canvas.create_oval(
                            (
                                circle_x - config.MOVE_MARK_SIZE_OFFSET,
                                circle_y - config.MOVE_MARK_SIZE_OFFSET,
                                circle_x + config.MOVE_MARK_SIZE_OFFSET,
                                circle_y + config.MOVE_MARK_SIZE_OFFSET,
                            ),
                            fill=config.MOVE_MARK_COLOR,
                            outline="",
                        ),
                    ]
                )

    def update_piece_position(self, piece_name: str, new_pos: List[int]):
        self.pieces[piece_name].pos = new_pos
        self.pieces_pos[piece_name] = new_pos

    def get_piece_from_position(self) -> str:
        pos = [self.selected_coordinates["board_x"], self.selected_coordinates["board_y"]]
        piece_name = [k for k, v in self.pieces_pos.items() if v == pos]
        if len(piece_name) > 0:
            piece_name = piece_name[0]
        return piece_name

    def create_select_rectangle(self):
        x = self.selected_coordinates["canvas_x"] - config.SQUARE_SIZE / 2
        y = self.selected_coordinates["canvas_y"] - config.SQUARE_SIZE / 2
        self.select_rect = self.canvas.create_rectangle(
            x,
            y,
            x + config.SQUARE_SIZE,
            y + config.SQUARE_SIZE,
            outline=config.SELECT_COLOR,
            width=config.SELECT_WIDTH,
        )

    def capture_piece(self):
        piece_name = self.get_piece_from_position()
        if piece_name:
            self.pieces.pop(piece_name)
            self.pieces_pos.pop(piece_name)
            subprocess.Popen(["afplay", constants.SOUND_FOLDER + "capture.wav"])
            print(f"Piece {piece_name} was captured")

    def move_piece(self, play_move_sound: bool=True):
        old_canvas_x, old_canvas_y = self.selected_item["canvas_xy"]
        piece = self.pieces[self.selected_item["piece"]]
        piece.move_piece(
            move_x=self.selected_coordinates["canvas_x"] - old_canvas_x,
            move_y=self.selected_coordinates["canvas_y"] - old_canvas_y,
        )
        self.update_piece_position(
            piece_name=self.selected_item["piece"], new_pos=[self.selected_coordinates["board_x"], self.selected_coordinates["board_y"]]
        )
        if play_move_sound:
            subprocess.Popen(["afplay", constants.SOUND_FOLDER + "move.wav"])
        self.is_selected = False
        self.white_turn = not self.white_turn

    def move_with_capture(self):
        self.capture_piece()
        self.move_piece(play_move_sound=False)

    def select_piece(self, piece_name):
        self.create_select_rectangle()
        self.selected_item["canvas_xy"] = [self.selected_coordinates["canvas_x"], self.selected_coordinates["canvas_y"]]
        self.selected_item["board_xy"] = [self.selected_coordinates["board_x"], self.selected_coordinates["board_y"]]
        self.selected_item["piece"] = piece_name
        self.selected_item["item_turn"] = piece_name.isupper() == self.white_turn
        self.is_selected = True
