import random, os
from datetime import datetime
from game_bot import CPU
from board import Board
from tweet_services import *

YOUR_TURN = "It's 𝗬𝗢𝗨𝗥 turn!"
MY_TURN = "It's 𝗠𝗬 turn!"
INCORRECT_INPUT = "I don't understand that response, reply something like:" \
                  "\nplay (number)"
BEEN_PLAYED = "Sorry! That space has been 𝗣𝗟𝗔𝗬𝗘𝗗 𝗔𝗟𝗥𝗘𝗔𝗗𝗬, pick another one!"
YOU_PLAYED = "𝗬𝗢𝗨 played: "
I_PLAYED = "𝗜 played: "
X = 'X'
O = 'O'

START_PLAY_AGAIN = "Reply with \"start\" to play again!"
YOU_WON = ["Congrats! You 𝗪𝗢𝗡! " + START_PLAY_AGAIN,
           "You won, congrats I guess 😒. " + START_PLAY_AGAIN,
           "You beat me, I can admit I lost! " + START_PLAY_AGAIN,
           "I'll beat you next time, don't you worry about it! " + START_PLAY_AGAIN]
I_WON = ["Haha! I 𝗪𝗢𝗡! " + START_PLAY_AGAIN,
         "I think you 𝗟𝗢𝗦𝗧, pal! " + START_PLAY_AGAIN,
         "I think I just 𝗪𝗢𝗡! " + START_PLAY_AGAIN,
         "You 𝗟𝗢𝗦𝗧! Better luck next time! " + START_PLAY_AGAIN]

DRAW = "It's a 𝗗𝗥𝗔𝗪!"
COMMAND_BEFORE_START = "You're trying to use a  game command without starting a game! " \
                    "Reply to this tweet with the command \"start\" to play!"
COME_AGAIN = "Sorry to see you go! Play again soon!"

def saveProgress(b, user):
    """
    Saves progress of Board into text file named after the user
    :param b: The board
    :param user: The player of the current board
    :return:
    """
    fileWrite = open("reference_files/" + user + ".txt", "w+")
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
    fileRead = open("reference_files/" + user + ".txt", 'r')
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

def iWonGIF(tweetID, user):
    gifSelector = str(random.randint(1, 4))
    gifName = "res/" + gifSelector + "iw.gif"
    msg = user + random.choice(I_WON)
    api.update_with_media(gifName, msg, in_reply_to_status_id=tweetID)

def youWonGIF(tweetID, user):
    gifSelector = str(random.randint(2, 6))
    gifName = "res/" + gifSelector + "il.gif"
    msg = user + random.choice(YOU_WON)
    api.update_with_media(gifName, msg, in_reply_to_status_id=tweetID)

def drawResponse(tweetID, user):
    gifSelector = str(1)
    gifName = "res/" + gifSelector + "il.gif"
    msg = user + DRAW
    api.update_with_media(gifName, msg, in_reply_to_status_id=tweetID)

def retweetWinner(tweetID):
    try:
        api.retweet(tweetID)
    except tweepy.error.TweepError:
        pass

def bot():
    """
    Loop runs to retrieve and process all new mentions
    """
    api.update_profile(description = "I am currently ONLINE, reply to my pinned to play!")
    while True:
        # pulls and processes new Tweets
        batch = getNewMentions()
        batchData = processTweetBatch(batch)[::-1]
        for dataset in batchData:  # for each dataset in the batch
            """
            dataset = {
                'cmd',
                'player',
                'id',
                'in_reply_to_id',
                'flag'}
            """
            current = datetime.now().strftime("%m/%d/%y, %H:%M:%S")
            print(dataset['player'], '-> ', "(" + dataset['cmd'] + ',', str(dataset['flag']) + ')', '-', current)
            if dataset['cmd'] == "start":
                # initializes the Board
                userBoard = Board()
                if dataset['flag'] is None:
                    userBoard.gameDifficulty = 'easy'
                elif dataset['flag'] == 'easy':
                    userBoard.gameDifficulty = 'easy'
                elif dataset['flag'] == 'medium':
                    userBoard.gameDifficulty = 'medium'
                elif dataset['flag'] == 'hard':
                    userBoard.gameDifficulty = 'hard'

                # determines if player is first
                # playerFirst = bool(random.getrandbits(1))
                playerFirst = False
                if playerFirst:
                    # replies that it's player's turn
                    replyBoardMessage(YOUR_TURN + str(userBoard), dataset['id'], dataset['player'])

                    # creates player save file
                    saveProgress(userBoard, dataset['player'])
                elif not playerFirst:
                    # plays CPU move on Board
                    CPU.playMove(userBoard, O)

                    # replies Board to Tweet
                    replyBoardMessage("I'll start, I'll be " + Board.O + ": " + str(userBoard), dataset['id'], dataset['player'], YOUR_TURN)

                    # saves the user's game progress
                    saveProgress(userBoard, dataset['player'])

            elif dataset['cmd'] == "play":
                try:
                    userBoard = loadProgress(dataset['player'])

                    # if the flag is valid and the move hasn't already been played
                    if 1 <= dataset['flag'] <= 9 and not userBoard.hasBeenPlayed(dataset['flag']):
                        userBoard.playMove(dataset['flag'], X)

                        # if the user won the game with their move
                        if userBoard.isWon():
                            # replies the current board and the WON message
                            botReply = replyBoardMessage(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard), dataset['id'], dataset['player'])
                            retweetWinner(botReply.id)
                            youWonGIF(botReply.id, dataset['player'] + " ")
                            # deletes the save file if the game is over
                            os.remove("reference_files/" + dataset["player"] + ".txt")

                        # if the user forced a draw on the game with their move
                        elif userBoard.isDraw():
                            # replies the current board and the DRAW message
                            botReply = replyBoardMessage(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard), dataset['id'], dataset['player'])
                            retweetWinner(botReply.id)
                            drawResponse(botReply.id, dataset['player'] + " ")
                            # deletes the save file if the game is over
                            os.remove("reference_files/" + dataset["player"] + ".txt")

                        # if the user's move doesn't cause the end of the game
                        else:
                            botReply = replyBoardMessage(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard), dataset['id'], dataset['player'], MY_TURN)
                            # the CPU plays the best move
                            CPU.playMove(userBoard, O)

                            # if the CPU won the game with their move
                            if userBoard.isWon():
                                # replies the current board and the WON message
                                botReply = replyBoardMessage(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard), botReply.id, dataset['player'])
                                retweetWinner(botReply.id)
                                iWonGIF(botReply.id, dataset['player'] + " ")
                                # deletes the save file if the game is over
                                os.remove("reference_files/" + dataset["player"] + ".txt")

                            # if the CPU forced a draw on the game with their move
                            elif userBoard.isDraw():
                                # replies the current board and the DRAW message
                                botReply = replyBoardMessage(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard), botReply.id, dataset['player'])
                                retweetWinner(botReply.id)
                                drawResponse(botReply.id, dataset['player'] + " ")
                                # deletes the save file if the game is over
                                os.remove("reference_files/" + dataset["player"] + ".txt")

                            # if the CPU's move doesn't cause the end of the game
                            else:
                                replyBoardMessage(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard), botReply.id, dataset['player'], YOUR_TURN)
                                # saves the user's game progress
                                saveProgress(userBoard, dataset['player'])
                    else:
                        # if the given command flag isn't valid
                        if not 1 <= dataset['flag'] <= 9:
                            replyMessage(INCORRECT_INPUT, dataset['id'], dataset['player'])

                        # if the given command flag has already been played
                        elif userBoard.hasBeenPlayed(dataset['flag']):
                            replyMessage(BEEN_PLAYED, dataset['id'], dataset['player'])

                # if the user tries to play a move on a game that hasn't started
                except FileNotFoundError:
                    replyMessage(COMMAND_BEFORE_START, dataset['id'], dataset['player'])

            #  TODO: Reference help thread
            elif dataset['cmd'] == "help":
                pass

            elif dataset['cmd'] == "quit":
                try:
                    os.remove("reference_files/" + dataset["player"] + ".txt")
                    replyMessage(COME_AGAIN, dataset['id'], dataset['player'])
                except OSError:
                    replyMessage(COMMAND_BEFORE_START, dataset['id'], dataset['player'])

            updateLastSeen(LAST_SEEN, dataset['id'])
        time.sleep(15)
        raise Exception("Test Error")

try:
    bot()
except KeyboardInterrupt:
    api.update_profile(description = "Sorry, I am OFFLINE right now.")
except Exception as e:
    api.update_profile(description="Sorry, I am OFFLINE right now.")
    # api.send_direct_message(963133317037154304, "BOT FAILURE: " + str(e))
    print("BOT FAILURE: " + str(e))
