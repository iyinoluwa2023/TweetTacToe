import random
from datetime import datetime
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
    batchData = process_tweet_batch(batch)[::-1]
    for dataset in batchData:  # for each dataset in the batch
        log_user(dataset)
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
                reply_board_message(YOUR_TURN + str(userBoard), dataset['id'],
                                    dataset['player'])  # replies that it's player's turn
                save_progress(userBoard, dataset['player'])  # creates player save file
            elif not playerFirst:
                CPU.play_move(userBoard, O)  # plays CPU move on Board
                reply_board_message("I'll start, I'll be " + Board.O + ": " + str(userBoard), dataset['id'],
                                    dataset['player'], YOUR_TURN)  # replies Board to Tweet
                save_progress(userBoard, dataset['player'])  # saves the user's game progress
        elif dataset['cmd'] == "play":
            try:
                userBoard = load_progress(dataset['player'])
                flagValid = (1 <= dataset['flag'] <= 9)
                hasBeenPlayed = userBoard.has_been_played(dataset['flag'])
                if flagValid and not hasBeenPlayed:
                    userBoard.play_move(dataset['flag'], X)  # if the flag is valid and the move hasn't already been
                    # played
                    if userBoard.is_won():  # if the user won the game with their move
                        botReply = reply_board_message(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                       dataset['id'],
                                                       dataset['player'])  # replies the current board and the WON message
                        retweet_winner(botReply.id)
                        reply_message(random.choice(YOU_WON), botReply.id, dataset['player'])
                        os.remove(cache + dataset[
                            "player"] + ".txt")  # deletes the save file if the game is over
                    elif userBoard.is_draw():  # if the user forced a draw on the game with their move
                        botReply = reply_board_message(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                       dataset['id'], dataset['player'])  # replies the current board
                        # and the DRAW message
                        retweet_winner(botReply.id)
                        reply_message(random.choice(DRAW), botReply.id, dataset['player'])
                        os.remove(cache + dataset["player"] + ".txt")  # deletes the save file if the
                        # game is over
                    else:  # if the user's move doesn't cause the end of the game
                        botReply = reply_board_message(YOU_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                       dataset['id'], dataset['player'], MY_TURN)
                        CPU.play_move(userBoard, O)  # the CPU plays the best move
                        if userBoard.is_won():  # if the CPU won the game with their move
                            botReply = reply_board_message(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                           botReply.id, dataset['player'])  # replies the current board
                            # and the WON message
                            retweet_winner(botReply.id)
                            reply_message(random.choice(I_WON), botReply.id, dataset['player'])
                            os.remove(cache + dataset[
                                "player"] + ".txt")  # deletes the save file if the game is over
                        elif userBoard.is_draw():  # if the CPU forced a draw on the game with their move

                            botReply = reply_board_message(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard),
                                                           botReply.id, dataset['player'])  # replies the current board
                            # and the DRAW message
                            retweet_winner(botReply.id)
                            reply_message(random.choice(DRAW), botReply.id, dataset['player'])
                            os.remove(cache + dataset["player"] + ".txt")  # deletes the save file if
                            # the game is over
                        else:  # if the CPU's move doesn't cause the end of the game
                            reply_board_message(I_PLAYED + str(userBoard.lastPlayed) + '\n' + str(userBoard), botReply.id,
                                                dataset['player'], YOUR_TURN)
                            save_progress(userBoard, dataset['player'])  # saves the user's game progress
                else:
                    if not flagValid:  # if the given command flag isn't valid
                        reply_message(INCORRECT_INPUT, dataset['id'], dataset['player'])
                    elif userBoard.has_been_played(dataset['flag']):  # if the given command flag has already been
                        # played
                        reply_message(BEEN_PLAYED, dataset['id'], dataset['player'])
            except FileNotFoundError:  # if the user tries to play a move on a game that hasn't started
                reply_message(COMMAND_BEFORE_START, dataset['id'], dataset['player'])
        elif dataset['cmd'] == "quit":
            try:
                os.remove(cache + dataset["player"] + ".txt")
                reply_message(COME_AGAIN, dataset['id'], dataset['player'])
            except OSError:
                reply_message(COMMAND_BEFORE_START, dataset['id'], dataset['player'])
        update_last_seen(dataset['id'])
        time.sleep(15)

def main():
    while True:
        try:
            bot()
            return {
                'statusCode' : 200
            }
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print("BOT FAILURE: " + str(e))

main()
