import os
import time
import tweepy
from dotenv import load_dotenv

load_dotenv()

auth = tweepy.OAuthHandler(os.environ['API_Key'], os.environ['API_Key_Secret'])
auth.set_access_token(os.environ['access_Key'], os.environ['access_Key_Secret'])
api = tweepy.API(auth, wait_on_rate_limit=True)

LAST_SEEN = "cache/last-seen.txt"
COMMANDS = ["start", "play", "quit", "help"]

def update_last_seen(lastSeenId):
    fileWrite = open(LAST_SEEN, 'w')
    fileWrite.write(str(lastSeenId))
    fileWrite.close()

def get_new_mentions():
    fileRead = open(LAST_SEEN, 'r')
    lastSeenId = int(fileRead.read().strip())
    fileRead.close()
    return api.mentions_timeline(lastSeenId, tweet_mode='extended')

def batch_delete(api):
    for status in tweepy.Cursor(api.user_timeline).items():
        try:
            api.destroy_status(status.id)
            print("Deleted:", status.id)
        except Exception:
            import traceback
            traceback.print_exc()
            print("Failed to delete:", status.id)

def process_tweet(tweet):
    """
    Takes tweets mentioning the bot and passes all relevant data into a dictionary
    :param tweet: a Tweet object
    :return: dictionary of all Tweet data
    """
    data = {'cmd': None,
            'player': None,
            'id': None,
            'flag': None}
    text = tweet.full_text.lower()
    parts = text.split()

    # if the tweet has more than 3 words then do not process
    if len(parts) <= 3 and parts[1] in COMMANDS:
        data['cmd'] = parts[1]
        data['player'] = "@" + tweet.user.screen_name
        data['id'] = tweet.id
        data['flag'] = None
        if len(parts) == 3:
            try:
                data['flag'] = int(parts[2])
            except ValueError:
                data['flag'] = parts[2]
        # updateLastSeen(LAST_SEEN, data['id'])
        return data
    return False

def process_tweet_batch(batch):
    """
    Processes all tweets in batch
    :param batch: group of Tweet objects
    :return: list of all processed tweet data dictionaries
    """
    allData = []
    for tweet in batch:
        if process_tweet(tweet):
            allData.append(process_tweet(tweet))
    return allData

def reply_message(msg, tweetID, player):
    try:
        time.sleep(3)
        msg = player + " " + msg
        return api.update_status(msg, tweetID)
    except tweepy.error.TweepError as e:
        print(e)

def reply_board_message(board, tweetID, player, message=None):
    try:
        time.sleep(3)
        if message:
            boardMsg = player + "\n" + str(board) + "\n\n" + message
        else:
            boardMsg = player + "\n" + str(board)
        return api.update_status(boardMsg, tweetID)
    except tweepy.error.TweepError as e:
        print(e)
