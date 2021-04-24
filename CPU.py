from board import Board
import copy
import random

class CPU:

    @staticmethod
    def win_from_next_move(b, playerSymbol):
        """
        Determines if the Player can win the game in their next move, and blocks that move if possible
        :param b: the game board
        :param playerSymbol: the symbol of the CPU, "O" or "X"
        :return: True if the CPU was able to make the move, False if the CPU was not able make the move
        """
        random.shuffle(b.available)

        if playerSymbol == 'O':
            otherSymbol = 'X'
        elif playerSymbol == 'X':
            otherSymbol = 'O'

        for i in b.available:
            bCopy = Board()
            bCopy.lastPlayed = b.lastPlayed
            bCopy.board = copy.deepcopy(b.board)
            bCopy.play_move(i, otherSymbol)
            if bCopy.is_won():
                b.play_move(i, playerSymbol)
                return True
        return False

    @staticmethod
    def opponent_win_from_next_move(b, playerSymbol):
        """
        Determines if the CPU can win the game in their next move, and plays that move if possible
        :param b: the game board
        :param playerSymbol: the symbol of the CPU, "O" or "X"
        :return: True if the CPU was able to make the move, False if the CPU was not able make the move
        """
        for i in b.available:
            bCopy = Board()
            bCopy.lastPlayed = b.lastPlayed
            bCopy.board = copy.deepcopy(b.board)
            bCopy.play_move(i, playerSymbol)
            if bCopy.is_won():
                b.play_move(i, playerSymbol)
                return True
        return False

    @staticmethod
    def take_corner(b, playerSymbol):
        random.shuffle(b.available)
        for i in b.available:
            if i in [1, 3, 7, 9]:
                b.play_move(i, playerSymbol)
                return True
        return False

    @staticmethod
    def take_center(b, playerSymbol):
        random.shuffle(b.available)
        if 5 in b.available:
            b.play_move(5, playerSymbol)
            return True
        return False

    @staticmethod
    def take_side(b, playerSymbol):
        random.shuffle(b.available)
        for i in b.available:
            if i in [2, 4, 6, 8]:
                b.play_move(i, playerSymbol)
                return True
        return False

    @staticmethod
    def play_move(b, playerSymbol):
        if b.gameDifficulty == 'easy':
            if CPU.take_corner(b, playerSymbol):
                return True
            if CPU.take_center(b, playerSymbol):
                return True
            if CPU.take_side(b, playerSymbol):
                return True
        if b.gameDifficulty == 'medium':
            if CPU.opponent_win_from_next_move(b, playerSymbol):
                return True
            if CPU.take_corner(b, playerSymbol):
                return True
            if CPU.take_center(b, playerSymbol):
                return True
            if CPU.take_side(b, playerSymbol):
                return True
        if b.gameDifficulty == 'hard':
            if CPU.win_from_next_move(b, playerSymbol):
                return True
            if CPU.opponent_win_from_next_move(b, playerSymbol):
                return True
            if CPU.take_corner(b, playerSymbol):
                return True
            if CPU.take_center(b, playerSymbol):
                return True
            if CPU.take_side(b, playerSymbol):
                return True
