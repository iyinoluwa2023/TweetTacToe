class Board:
    X = '\U0000274C'
    O = '\U0001F535'
    BLANK = '\U000026AA'
    NUMBERS = ['\U00000031\U0000FE0F\U000020E3',
               '\U00000032\U0000FE0F\U000020E3',
               '\U00000033\U0000FE0F\U000020E3',
               '\U00000034\U0000FE0F\U000020E3',
               '\U00000035\U0000FE0F\U000020E3',
               '\U00000036\U0000FE0F\U000020E3',
               '\U00000037\U0000FE0F\U000020E3',
               '\U00000038\U0000FE0F\U000020E3',
               '\U00000039\U0000FE0F\U000020E3',]

    def __init__(self):
        board = {}
        for i in range(len(Board.NUMBERS)):
            board[i + 1] = Board.BLANK
        self.board = board
        self.available = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.lastPlayed = None
        self.gameDifficulty= "easy"

    def __str__(self):
        s = "\n+----+----+----+\n"
        for position in self.board:
            if self.board[position] == Board.BLANK:
                s += '|' + f'{Board.NUMBERS[position - 1]: ^7}'
            else:
                s += '|' + f'{self.board[position]: ^5}'
            if position % 3 == 0:
                s += "|\n+----+----+----+\n"
        return s

    def hasBeenPlayed(self, position):
        beenPlayed = self.board[position] != Board.BLANK
        return True if beenPlayed else False

    def playMove(self, position: int, player: str) -> bool:
        """
        Plays move on the board
        :param position: position of move to be played
        :param player: symbol to be placed at move position
        :return: True if move was successful, False if unsucessful
        """
        if self.hasBeenPlayed(position):
            return False
        try:
            if 1 <= position <= 9:
                if player == 'O':
                    self.board[position] = Board.O
                    self.__updateAvailable()
                    self.lastPlayed = position
                elif player == 'X':
                    self.board[position] = Board.X
                    self.__updateAvailable()
                    self.lastPlayed = position
                return True
        except KeyError:
            return False
        return False

    def __updateAvailable(self):
        """
        Updates the list of available spaces left on the board
        """
        self.available = []
        for i in self.board:
            if self.board[i] == Board.BLANK:
                self.available.append(i)

    @staticmethod
    def __diagonalPositions(position):
        """
        Determines all possible diagonal positions of a given position
        :param position: any given position on the board
        :return: dictionary of with directions as key and position as values
        """
        boardMatrix = [[(i + 1 + (3*j)) for i in range(3)] for j in range(3)]
        diagonals = {
            'bottomLeft': None,
            'bottomRight': None,
            'topRight': None,
            'topLeft': None
        }
        for y, i in enumerate(boardMatrix):
            for x, j in enumerate(i):
                if j == position:
                    if 0 <= (y + 1) <= 2 and 0 <= (x - 1) <= 2:
                        diagonals['bottomLeft'] = boardMatrix[y + 1][x - 1]
                    if 0 <= (y + 1) <= 2 and 0 <= (x + 1) <= 2:
                        diagonals['bottomRight'] = boardMatrix[y + 1][x + 1]
                    if 0 <= (y - 1) <= 2 and 0 <= (x - 1) <= 2:
                        diagonals['topLeft'] = boardMatrix[y - 1][x - 1]
                    if 0 <= (y - 1) <= 2 and 0 <= (x + 1) <= 2:
                        diagonals['topRight'] = boardMatrix[y - 1][x + 1]
        return diagonals

    @staticmethod
    def __horizontalPositions(position):
        """
        Returns list of a positions to check from a given position
        :param position: Any given position on the board
        :return: list of possible horizontal positions
        """
        if 1 <= position <= 3:
            return [1, 2, 3]
        if 4 <= position <= 6:
            return [4, 5, 6]
        if 7 <= position <= 9:
            return [7, 8, 9]

    @staticmethod
    def __verticalPositions(position):
        """
        Returns list of a positions to check from a given position
        :param position: Any given position on the board
        :return: list of possible vertical positions
        """
        if position == 1 or position == 4 or position == 7:
            return [1, 4, 7]
        if position == 2 or position == 5 or position == 8:
            return [2, 5, 8]
        if position == 3 or position == 6 or position == 9:
            return [3, 6, 9]

    def __checkDiagonalWin(self):
        """
        Checks if the last played position creates a diagonal win
        :return: True if a diagonal win is achieved, False if not
        """
        diagonals = self.__diagonalPositions(self.lastPlayed)
        checkSymbol = self.board[self.lastPlayed]
        if self.lastPlayed == 5:
            if self.board[diagonals['topRight']] == checkSymbol and self.board[diagonals['bottomLeft']] == checkSymbol:
                return True
            if self.board[diagonals['topLeft']] == checkSymbol and self.board[diagonals['bottomRight']] == checkSymbol:
                return True
        for direction in diagonals:
            if diagonals[direction] and self.board[diagonals[direction]] == checkSymbol:
                try:
                    finalPosition = self.__diagonalPositions(diagonals[direction])[direction]
                    if self.board[finalPosition] == checkSymbol:
                        return True
                except KeyError:
                    pass
        return False

    def __checkHorizontalWin(self):
        """
        Checks if the last played position creates a horizontal win
        :return: True if a horizontal win is achieved, False if not
        """
        horizontals = self.__horizontalPositions(self.lastPlayed)
        checkSymbol = self.board[self.lastPlayed]
        for i in horizontals:
            if self.board[i] != checkSymbol:
                return False
        return True

    def __checkVerticalWin(self):
        """
        Checks if the last played position creates a vertical win
        :return: True if a vertical win is achieved, False if not
        """
        verticals = self.__verticalPositions(self.lastPlayed)
        checkSymbol = self.board[self.lastPlayed]
        for i in verticals:
            if self.board[i] != checkSymbol:
                return False
        return True

    def isWon(self):
        """
        Checks if last played position creates a win in all directions
        :return: True if a win is achieved, False if not
        """
        return True if (self.__checkHorizontalWin() or self.__checkVerticalWin() or self.__checkDiagonalWin()) else False

    def isDraw(self):
        for i in self.board:
            if self.board[i] == Board.BLANK:
                return False
        return True
