import random
import sys
import time
from datetime import datetime
import logging

import tweepy
from urllib3.connectionpool import xrange

from CPU import CPU
from string_constants import *
from tweet_services import *

cache = "cache/"

def log_user(dataset):
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
    batch = get_new_mentions()  # pulls and processes new Tweets
    commandsInBatch = process_tweet_batch(batch)[::-1]
    for command in commandsInBatch:  # for each command in the batch
        log_user(command)
        if command['cmd'] == "start":
            userBoard = Board()  # initializes the Board
            if command['flag'] is None:
                userBoard.gameDifficulty = 'easy'
            elif command['flag'] == 'easy':
                userBoard.gameDifficulty = 'easy'
            elif command['flag'] == 'medium':
                userBoard.gameDifficulty = 'medium'
            elif command['flag'] == 'hard':
                userBoard.gameDifficulty = 'hard'
            playerFirst = bool(random.getrandbits(1))  # determines if player is first
            if playerFirst:
                reply_board_message(YOUR_TURN + str(userBoard), command['id'],
                                    command['player'])  # replies that it's player's turn
                save_progress(userBoard, command['player'])  # creates player save file
            elif not playerFirst:
                CPU.play_move(userBoard, O)  # plays CPU move on Board
                reply_board_message("I'll start, I'll be " + Board.O + ": " + str(userBoard), command['id'],
                                    command['player'], YOUR_TURN)  # replies Board to Tweet
                save_progress(userBoard, command['player'])  # saves the user's game progress
        elif command['cmd'] == "play":
            try:
                userBoard = load_progress(command['player'])
                flagValid = (1 <= command['flag'] <= 9)
                hasBeenPlayed = userBoard.has_been_played(command['flag'])
                if flagValid and not hasBeenPlayed:
                    userBoard.play_move(command['flag'], X)  # if the flag is valid and the move hasn't already been
                    # played
                    if userBoard.is_won():  # if the user won the game with their move
                        botReply = reply_board_message(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                       command['id'],
                                                       command['player'])  # replies the current board and the WON message
                        retweet_winner(botReply.id)
                        reply_message(random.choice(YOU_WON), botReply.id, command['player'])
                        os.remove(cache + command[
                            "player"] + ".txt")  # deletes the save file if the game is over
                    elif userBoard.is_draw():  # if the user forced a draw on the game with their move
                        botReply = reply_board_message(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                       command['id'], command['player'])  # replies the current board
                        # and the DRAW message
                        retweet_winner(botReply.id)
                        reply_message(random.choice(DRAW), botReply.id, command['player'])
                        os.remove(cache + command["player"] + ".txt")  # deletes the save file if the
                        # game is over
                    else:  # if the user's move doesn't cause the end of the game
                        botReply = reply_board_message(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                       command['id'], command['player'], MY_TURN)
                        CPU.play_move(userBoard, O)  # the CPU plays the best move
                        if userBoard.is_won():  # if the CPU won the game with their move
                            botReply = reply_board_message(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                           botReply.id, command['player'])  # replies the current board
                            # and the WON message
                            retweet_winner(botReply.id)
                            reply_message(random.choice(I_WON), botReply.id, command['player'])
                            os.remove(cache + command[
                                "player"] + ".txt")  # deletes the save file if the game is over
                        elif userBoard.is_draw():  # if the CPU forced a draw on the game with their move

                            botReply = reply_board_message(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                           botReply.id, command['player'])  # replies the current board
                            # and the DRAW message
                            retweet_winner(botReply.id)
                            reply_message(random.choice(DRAW), botReply.id, command['player'])
                            os.remove(cache + command["player"] + ".txt")  # deletes the save file if
                            # the game is over
                        else:  # if the CPU's move doesn't cause the end of the game
                            reply_board_message(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard), botReply.id,
                                                command['player'], YOUR_TURN)
                            save_progress(userBoard, command['player'])  # saves the user's game progress
                else:
                    if not flagValid:  # if the given command flag isn't valid
                        reply_message(INCORRECT_INPUT, command['id'], command['player'])
                    elif userBoard.has_been_played(command['flag']):  # if the given command flag has already been
                        # played
                        reply_message(BEEN_PLAYED, command['id'], command['player'])
            except FileNotFoundError:  # if the user tries to play a move on a game that hasn't started
                reply_message(COMMAND_BEFORE_START, command['id'], command['player'])
        elif command['cmd'] == "quit":
            try:
                os.remove(cache + command["player"] + ".txt")
                reply_message(COME_AGAIN, command['id'], command['player'])
            except OSError:
                reply_message(COMMAND_BEFORE_START, command['id'], command['player'])
        update_last_seen(command['id'])
        time.sleep(240)

def main():
    while True:
        try:
            bot()
        except Exception as e:
            logging.exception("BOT FAILURE")

main()
