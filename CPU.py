from board import Board
import copy
import random

class CPU:

    @staticmethod
    def winFromNextMove(b, playerSymbol):
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
            bCopy.playMove(i, otherSymbol)
            if bCopy.isWon():
                b.playMove(i, playerSymbol)
                return True
        return False

    @staticmethod
    def opponentWinFromNextMove(b, playerSymbol):
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
            bCopy.playMove(i, playerSymbol)
            if bCopy.isWon():
                b.playMove(i, playerSymbol)
                return True
        return False

    @staticmethod
    def takeCorner(b, playerSymbol):
        random.shuffle(b.available)
        for i in b.available:
            if i in [1, 3, 7, 9]:
                b.playMove(i, playerSymbol)
                return True
        return False

    @staticmethod
    def takeCenter(b, playerSymbol):
        random.shuffle(b.available)
        if 5 in b.available:
            b.playMove(5, playerSymbol)
            return True
        return False

    @staticmethod
    def takeSide(b, playerSymbol):
        random.shuffle(b.available)
        for i in b.available:
            if i in [2, 4, 6, 8]:
                b.playMove(i, playerSymbol)
                return True
        return False

    @staticmethod
    def playMove(b, playerSymbol):
        if b.gameDifficulty == 'easy':
            if CPU.takeCorner(b, playerSymbol):
                return True
            if CPU.takeCenter(b, playerSymbol):
                return True
            if CPU.takeSide(b, playerSymbol):
                return True
        if b.gameDifficulty == 'medium':
            if CPU.opponentWinFromNextMove(b, playerSymbol):
                return True
            if CPU.takeCorner(b, playerSymbol):
                return True
            if CPU.takeCenter(b, playerSymbol):
                return True
            if CPU.takeSide(b, playerSymbol):
                return True
        if b.gameDifficulty == 'hard':
            if CPU.winFromNextMove(b, playerSymbol):
                return True
            if CPU.opponentWinFromNextMove(b, playerSymbol):
                return True
            if CPU.takeCorner(b, playerSymbol):
                return True
            if CPU.takeCenter(b, playerSymbol):
                return True
            if CPU.takeSide(b, playerSymbol):
                return True
