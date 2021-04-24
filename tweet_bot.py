import os
import random
from datetime import datetime

from board import Board
from CPU import CPU
from string_constants import *
from tweet_services import *

cache = "tmp/"

def saveProgress(b, user):
    """
    Saves progress of Board into text file named after the user
    :param b: The board
    :param user: The player of the current board
    :return:
    """
    fileWrite = open(cache + user + ".txt", "w+")
    for position in b.board:
        if b.board[position] is not None:
            fileWrite.write(str(position) + " " + str(b.board[position]) + "\n")
        else:
            fileWrite.write(str(position) + " " + "0" + "\n")
    fileWrite.write(str(b.available) + "\n")
    fileWrite.write(str(b.lastPlayed) + "\n")
    fileWrite.write(b.gameDifficulty)
    fileWrite.close()


def loadProgress(user):
    """
    Reads file named after user to create Board object
    :param user: the user who owns the board
    :return: the loaded Board object
    """
    b = Board()
    loadAvailable = []
    loadBoard = {}
    fileRead = open(cache + user + ".txt", 'r')
    lines = tuple(fileRead)
    for i in range(0, 9):
        line = lines[i]
        dictKey = int(line[0])
        dictVal = line[2]
        if dictVal == 0:
            loadBoard[dictKey] = dictKey
        else:
            loadBoard[dictKey] = dictVal
    for i in lines[9]:
        try:
            loadAvailable.append(int(i))
        except ValueError:
            pass
    try:
        loadLastPlayed = int(lines[10])
    except ValueError:
        loadLastPlayed = None
    loadDifficulty = lines[11]
    b.gameDifficulty = loadDifficulty
    b.available = loadAvailable
    b.lastPlayed = loadLastPlayed
    b.board = loadBoard
    fileRead.close()
    return b


def retweetWinner(tweetID):
    try:
        api.retweet(tweetID)
    except tweepy.error.TweepError:
        pass


def logUser(dataset):
    current = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
    currPlayer = dataset['player']
    currCmd = dataset['cmd']
    currFlag = str(dataset['flag'])
    log = f'{currPlayer : <20} -> {currCmd : <5}, {currFlag : <5} - {current}'
    print(log)


def bot():
    """
    Loop runs to retrieve and process all new mentions
    """
    print()
    api.update_profile(description="I am currently ONLINE, reply to my pinned to play!")
    batch = getNewMentions()  # pulls and processes new Tweets
    batchData = processTweetBatch(batch)[::-1]
    for dataset in batchData:  # for each dataset in the batch
        logUser(dataset)
        if dataset['cmd'] == "start":
            userBoard = Board()  # initializes the Board
            if dataset['flag'] is None:
                userBoard.gameDifficulty = 'easy'
            elif dataset['flag'] == 'easy':
                userBoard.gameDifficulty = 'easy'
            elif dataset['flag'] == 'medium':
                userBoard.gameDifficulty = 'medium'
            elif dataset['flag'] == 'hard':
                userBoard.gameDifficulty = 'hard'
            playerFirst = bool(random.getrandbits(1))  # determines if player is first
            if playerFirst:
                replyBoardMessage(YOUR_TURN + str(userBoard), dataset['id'],
                                  dataset['player'])  # replies that it's player's turn
                saveProgress(userBoard, dataset['player'])  # creates player save file
            elif not playerFirst:
                CPU.playMove(userBoard, O)  # plays CPU move on Board
                replyBoardMessage("I'll start, I'll be " + Board.O + ": " + str(userBoard), dataset['id'],
                                  dataset['player'], YOUR_TURN)  # replies Board to Tweet
                saveProgress(userBoard, dataset['player'])  # saves the user's game progress
        elif dataset['cmd'] == "play":
            try:
                userBoard = loadProgress(dataset['player'])
                flagValid = (1 <= dataset['flag'] <= 9)
                hasBeenPlayed = userBoard.hasBeenPlayed(dataset['flag'])
                if flagValid and not hasBeenPlayed:
                    userBoard.playMove(dataset['flag'], X)  # if the flag is valid and the move hasn't already been
                    # played
                    if userBoard.isWon():  # if the user won the game with their move
                        botReply = replyBoardMessage(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                     dataset['id'],
                                                     dataset['player'])  # replies the current board and the WON message
                        retweetWinner(botReply.id)
                        replyMessage(random.choice(YOU_WON), botReply.id, dataset['player'])
                        os.remove(cache + dataset[
                            "player"] + ".txt")  # deletes the save file if the game is over
                    elif userBoard.isDraw():  # if the user forced a draw on the game with their move
                        botReply = replyBoardMessage(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                     dataset['id'], dataset['player'])  # replies the current board
                        # and the DRAW message
                        retweetWinner(botReply.id)
                        replyMessage(random.choice(DRAW), botReply.id, dataset['player'])
                        os.remove(cache + dataset["player"] + ".txt")  # deletes the save file if the
                        # game is over
                    else:  # if the user's move doesn't cause the end of the game
                        botReply = replyBoardMessage(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                     dataset['id'], dataset['player'], MY_TURN)
                        CPU.playMove(userBoard, O)  # the CPU plays the best move
                        if userBoard.isWon():  # if the CPU won the game with their move
                            botReply = replyBoardMessage(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                         botReply.id, dataset['player'])  # replies the current board
                            # and the WON message
                            retweetWinner(botReply.id)
                            replyMessage(random.choice(I_WON), botReply.id, dataset['player'])
                            os.remove(cache + dataset[
                                "player"] + ".txt")  # deletes the save file if the game is over
                        elif userBoard.isDraw():  # if the CPU forced a draw on the game with their move

                            botReply = replyBoardMessage(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                         botReply.id, dataset['player'])  # replies the current board
                            # and the DRAW message
                            retweetWinner(botReply.id)
                            replyMessage(random.choice(DRAW), botReply.id, dataset['player'])
                            os.remove(cache + dataset["player"] + ".txt")  # deletes the save file if
                            # the game is over
                        else:  # if the CPU's move doesn't cause the end of the game
                            replyBoardMessage(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard), botReply.id,
                                              dataset['player'], YOUR_TURN)
                            saveProgress(userBoard, dataset['player'])  # saves the user's game progress
                else:
                    if not flagValid:  # if the given command flag isn't valid
                        replyMessage(INCORRECT_INPUT, dataset['id'], dataset['player'])
                    elif userBoard.hasBeenPlayed(dataset['flag']):  # if the given command flag has already been played
                        replyMessage(BEEN_PLAYED, dataset['id'], dataset['player'])
            except FileNotFoundError:  # if the user tries to play a move on a game that hasn't started
                replyMessage(COMMAND_BEFORE_START, dataset['id'], dataset['player'])
        elif dataset['cmd'] == "quit":
            try:
                os.remove(cache + dataset["player"] + ".txt")
                replyMessage(COME_AGAIN, dataset['id'], dataset['player'])
            except OSError:
                replyMessage(COMMAND_BEFORE_START, dataset['id'], dataset['player'])
        updateLastSeen(LAST_SEEN, dataset['id'])


while True:
    try:
        bot()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("BOT FAILURE: " + str(e))