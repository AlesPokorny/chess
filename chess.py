import subprocess
import tkinter as tk
from typing import List, Type
import sys
import numpy as np
import os
import config
import constants
from pieces import Piece
from utils import calculate_board_coordinates_from_canvas, calculate_canvas_coordinates_from_board

import platform

if platform.system() == "Windows":
    import winsound


class Chess:
    def __init__(self, windows: bool):
        self.windows = windows
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
        self.in_game = True
        self.en_passant = []

    def run(self):
        self.init_pieces()
        self.get_all_possible_moves()
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
            for column_number, _ in enumerate(row):
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
        if self.in_game:
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
            if self.is_selected & self.selected_item["item_turn"] and len(self.possible_moves) > 0:
                if [
                    self.selected_coordinates["board_x"],
                    self.selected_coordinates["board_y"],
                ] in self.possible_moves:
                    if piece_name:
                        self.move_with_capture()
                    elif [self.selected_coordinates["board_x"], self.selected_coordinates["board_y"]] == self.en_passant:
                        self.en_passant_capture()
                    else:
                        self.move_piece()
                        self.play_sound(sound="move")
                else:
                    if piece_name:
                        self.select_piece(piece_name=piece_name)
                        if self.selected_item["item_turn"]:
                            self.draw_possible_moves(piece_name)
            else:
                if piece_name:
                    self.select_piece(piece_name=piece_name)
                    if self.selected_item["item_turn"]:
                        self.draw_possible_moves(piece_name)
                else:
                    self.create_select_rectangle()
                    self.is_selected = False

    def get_all_possible_moves(self) -> List:
        all_moves = []
        for piece_name in self.pieces:
            if self.pieces[piece_name].is_white == self.white_turn:
                possible_moves = self.get_possible_moves_per_piece(piece_name=piece_name)
                self.pieces[piece_name].possible_moves = possible_moves
                if len(possible_moves) > 0:
                    all_moves.append(possible_moves)
        return all_moves

    def get_possible_moves_per_piece(self, piece_name: str) -> List:
        possible_moves = self.pieces[piece_name].calculate_possible_moves(pieces_pos=self.pieces_pos, en_passant=self.en_passant)
        if len(possible_moves) > 0:
            possible_moves = self.filter_illegal_moves(moves=possible_moves, piece_name=piece_name)
        return possible_moves

    def filter_illegal_moves(self, moves: List, piece_name: str) -> List:
        original_position = self.pieces[piece_name].pos
        if self.white_turn:
            king_position = self.pieces_pos["K0"]
        else:
            king_position = self.pieces_pos["k0"]

        legal_moves = []

        for move in moves:
            illegal_move = False
            self.pieces[piece_name].pos = move
            self.pieces_pos[piece_name] = move

            if piece_name in ["k0", "K0"]:
                king_position = move

            for piece in self.pieces:
                if self.pieces[piece].is_white != self.white_turn:
                    possible_moves = self.pieces[piece].calculate_possible_moves(pieces_pos=self.pieces_pos)

                    king_capture_moves = [
                        possible_move
                        for possible_move in possible_moves
                        if possible_move == king_position and move != self.pieces[piece].pos
                    ]
                    if len(king_capture_moves) > 0:
                        illegal_move = True
                        break

            if not illegal_move:
                legal_moves.append(move)

        self.pieces[piece_name].pos = original_position
        self.pieces_pos[piece_name] = original_position

        return legal_moves

    def remove_possible_move_marks(self):
        if len(self.possible_move_mark):
            for mark_to_delete in self.possible_move_mark:
                self.canvas.delete(mark_to_delete)
            self.possible_move_mark = []

    def draw_possible_moves(self, piece_name):
        self.possible_moves = self.pieces[piece_name].possible_moves

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
        pos = [
            self.selected_coordinates["board_x"],
            self.selected_coordinates["board_y"],
        ]
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

    def play_sound(self, sound):
        if sound == "move":
            if self.windows:
                winsound.PlaySound(constants.SOUND_FOLDER + constants.SOUND_MOVE_FILE, winsound.SND_FILENAME)
            else:
                subprocess.Popen(["afplay", constants.SOUND_FOLDER + constants.SOUND_MOVE_FILE])

        elif sound == "capture":
            if self.windows:
                winsound.PlaySound(constants.SOUND_FOLDER + constants.SOUND_CAPTURE_FILE, winsound.SND_FILENAME)
            else:
                subprocess.Popen(["afplay", constants.SOUND_FOLDER + constants.SOUND_CAPTURE_FILE])

    def capture_piece(self):
        piece_name = self.get_piece_from_position()
        if piece_name:
            self.pieces.pop(piece_name)
            self.pieces_pos.pop(piece_name)
            print(f"Piece {piece_name} was captured")

    def move_piece(self):
        old_canvas_x, old_canvas_y = self.selected_item["canvas_xy"]
        piece = self.pieces[self.selected_item["piece"]]
        if piece.piece.lower() == "p":
            self.allow_en_passant()
        else:
            self.en_passant = []

        piece.move_piece(
            move_x=self.selected_coordinates["canvas_x"] - old_canvas_x,
            move_y=self.selected_coordinates["canvas_y"] - old_canvas_y,
        )
        self.update_piece_position(
            piece_name=self.selected_item["piece"],
            new_pos=[
                self.selected_coordinates["board_x"],
                self.selected_coordinates["board_y"],
            ],
        )
        self.is_selected = False
        self.white_turn = not self.white_turn
        all_moves = self.get_all_possible_moves()
        if len(all_moves) == 0:
            self.show_winning_screen()

    def allow_en_passant(self):
        is_correct_rank = self.selected_coordinates["board_y"] in [3, 4]
        if is_correct_rank:
            was_moved_by_two = abs(self.selected_coordinates["board_y"] - self.selected_item["board_xy"][1]) == 2
            if was_moved_by_two:
                x = self.selected_coordinates["board_x"]
                y = self.selected_coordinates["board_y"]
                if self.white_turn:
                    y = y + 1
                else:
                    y = y - 1
                self.en_passant = [x, y]
        else:
            self.en_passant = []

    def en_passant_capture(self):
        board_y = self.selected_coordinates["board_y"]
        if self.white_turn:
            self.selected_coordinates["board_y"] = board_y + 1
        else:
            self.selected_coordinates["board_y"] = board_y - 1
        self.capture_piece()
        self.selected_coordinates["board_y"] = board_y
        self.move_piece()

    def move_with_capture(self):
        self.capture_piece()
        self.move_piece()
        self.play_sound(sound="capture")

    def select_piece(self, piece_name):
        self.create_select_rectangle()
        self.selected_item["canvas_xy"] = [
            self.selected_coordinates["canvas_x"],
            self.selected_coordinates["canvas_y"],
        ]
        self.selected_item["board_xy"] = [
            self.selected_coordinates["board_x"],
            self.selected_coordinates["board_y"],
        ]
        self.selected_item["piece"] = piece_name
        self.selected_item["item_turn"] = piece_name.isupper() == self.white_turn
        self.is_selected = True

    def show_winning_screen(self):
        self.in_game = False
        if self.white_turn:
            winning_color = "White"
        else:
            winning_color = "Black"
        self.canvas.delete("all")
        self.canvas.create_text(
            (config.BOARD_SIZE / 2, config.BOARD_SIZE / 2), text=f"{winning_color} won", anchor="center", font="Helvetica 18 bold"
        )

    def restart(self):
        self.tk_root.destroy()
        os.startfile("main.py")

    def quit(self):
        self.tk_root.destroy()
        sys.exit(0)
